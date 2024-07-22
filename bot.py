import discord
from discord.ext import commands, tasks
import requests
import random
import time

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

USER_TO_MONITOR = 'felixband'
GIF_SERVICES = ['https://tenor.com', 'https://giphy.com', 'https://imgur.com', 'https://cdn.discord.com']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    change_status.start()  # Start the task to change status

def get_random_game_name():
    while True:
        # Get a random appid between 1 and 999999
        appid = random.randint(1, 999999)
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if str(appid) in data and data[str(appid)]['success']:
                game_name = data[str(appid)]['data']['name']
                return game_name
        time.sleep(1)  # Avoid hammering the API

@tasks.loop(minutes=30)
async def change_status():
    game_name = get_random_game_name()
    await bot.change_presence(activity=discord.Game(name=game_name))
    print(f'Changed status to: Playing {game_name}')

@bot.event
async def on_message(message):
    if message.author.name == USER_TO_MONITOR:
        for gif_service in GIF_SERVICES:
            if message.content.startswith(gif_service):
                await message.reply("epic embed fail")
                break
    if bot.user.mentioned_in(message):
        await message.channel.send("Hello! I'm here!")

with open('api-key.txt', 'r') as file:
    api_key = file.read().strip()

bot.run(api_key)
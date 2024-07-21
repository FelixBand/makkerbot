import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import random

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

STEAM_API_KEY = 'YOUR_STEAM_API_KEY'  # Replace with your Steam API key

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    change_status.start()  # Start the task to change status

async def get_random_game_name():
    while True:
        # Get a random appid between 1 and 999999
        appid = random.randint(1, 999999)
        async with aiohttp.ClientSession() as session:
            url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if str(appid) in data and data[str(appid)]['success']:
                        game_name = data[str(appid)]['data']['name']
                        return game_name
                await asyncio.sleep(1)  # Avoid hammering the API

@tasks.loop(minutes=30)
async def change_status():
    game_name = await get_random_game_name()
    await bot.change_presence(activity=discord.Game(name=game_name))
    print(f'Changed status to: Playing {game_name}')

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send("Hello! I'm here!")

with open('api-key.txt', 'r') as file:
    api_key = file.read().strip()

bot.run(api_key)
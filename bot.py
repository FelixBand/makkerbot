import discord
from discord.ext import commands, tasks
import requests
import random
import time
import os
from datetime import datetime, time as datetime_time
import praw

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

USER_TO_MONITOR = 'ltsbeary'
GIF_SERVICES = ['https://tenor.com', 'https://giphy.com', 'https://imgur.com', 'https://cdn.discord.com']
MEME_CHANNEL_ID = 1120692192990744658 #1066079471439978551

REDDIT_CLIENT_ID = 'YOUR_REDDIT_CLIENT_ID'
REDDIT_CLIENT_SECRET = 'YOUR_REDDIT_CLIENT_SECRET'
REDDIT_USER_AGENT = 'YOUR_USER_AGENT'

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    change_status.start()  # Start the task to change status
    #post_meme.start()  # Start the task to post memes

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

def load_responses(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

general_responses = load_responses('responses/responses.txt')

def get_personal_response(user_name):
    personal_file_path = f'responses/responses-{user_name}.txt'
    if os.path.exists(personal_file_path):
        if random.random() < 0.3:  # 30% chance
            return load_responses(personal_file_path)
    return general_responses

@bot.event
async def on_message(message):
    if message.author.name == USER_TO_MONITOR:
        for gif_service in GIF_SERVICES:
            if message.content.startswith(gif_service):
                await message.reply("epic embed fail")
                break
    if bot.user.mentioned_in(message):
        responses = get_personal_response(message.author.name)
        response = random.choice(responses)
        await message.reply(response.strip())

def get_random_meme():
    subreddit = reddit.subreddit("memes")
    meme_list = list(subreddit.hot(limit=50))  # Fetch top 50 hot posts
    meme = random.choice(meme_list)
    return meme.url

@tasks.loop(hours=5)
async def post_meme():
    current_time = datetime.now().time()
    start_time = datetime_time(11, 0)  # 11:00
    end_time = datetime_time(21, 0)    # 21:00
    if start_time <= current_time <= end_time:
        meme_channel = bot.get_channel(MEME_CHANNEL_ID)
        if meme_channel is not None:
            meme_url = get_random_meme()
            await meme_channel.send(meme_url)
            print(f'Posted meme: {meme_url}')
        else:
            print(f'Channel with ID {MEME_CHANNEL_ID} not found.')

with open('api-key.txt', 'r') as file:
    api_key = file.read().strip()

bot.run(api_key)
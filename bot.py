import discord
from discord.ext import commands

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):  # Check if bot is mentioned in the message
        pass

with open('api-key.txt', 'r') as file: # Gotta be careful not to leak this one. Trusting gitignore
    api_key = file.read().strip()

# Now, use the content of the file with bot.run()
bot.run(api_key)
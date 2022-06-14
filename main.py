import discord
import os
from discord.ext import commands
import music
from keep_alive import keep_alive

print('Test point 1')
cogs = [music]

client = commands.Bot(command_prefix='!dj ', intents = discord.Intents.all())
print('Test Point 2')
for i in range(len(cogs)):
  cogs[i].setup(client)

print('hi')
keep_alive()
client.run(os.environ['TOKEN'])

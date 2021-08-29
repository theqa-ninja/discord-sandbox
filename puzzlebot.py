import discord
import json
import pdb
import os
from discord.ext import commands


client = MyClient()
bot_intents = discord.Intents.default()
bot_intents.members = True
bot_intents.presences = True
client = commands.Bot(command_prefix = '$', intents=bot_intents)
client.run(token)

from discord_slash import SlashCommand
import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", case_insinsative=True, intents=intents)
intents.members=True
slash = SlashCommand(bot, sync_commands = True, sync_on_cog_reload = True) 
bot.remove_command("help")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("ODgzMTMzMzM1ODI2NzUxNTA4.YTFgAw.G-j1rzwxlYq6b0FnnF4pvwdCV8s")
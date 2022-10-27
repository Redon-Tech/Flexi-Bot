import discord
import discord.ext.commands
import os
from glob import glob

bot = discord.ext.commands.Bot(intents=discord.Intents.all(), command_prefix="!")
cogs = [path.split("/")[-1][:-3] for path in glob("./cogs/*.py")]

@bot.event
async def on_ready():
  global stdout
  stdout = bot.get_channel(852271893771845733)
  await stdout.purge(limit=100)

  await stdout.send("`Loading cogs`")
  print("Loading cogs")
  for cog in cogs:
    bot.load_extension(f"cogs.{cog}")
    await stdout.send(f"` {cog} loaded`")
    print(f" {cog} loaded")

  await stdout.send("`Bot ready`")
  print("Bot ready\n Logged in as: " + bot.user.name + "For " + bot.guilds[0].name + "Server's" ) 
  print(bot.user.name + " is Now Online for " + bot.guilds[0].name + "Server's" + " with " + str(len(bot.users)) + " Users")
bot.run(os.getenv("token"))
import pathlib
import asyncio

import discord

from ext import setup, reload_cogs

# setting up bot
token = pathlib.Path("token.txt").read_text().strip()
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print("---- bot ----")
    print("name:", bot.user.name)
    print("id:", bot.user.id)
    print("-------------")


@bot.slash_command(guild_ids=[942318419011833896])
async def reload(ctx: discord.ApplicationContext):
    reload_cogs(bot)
    await ctx.respond("Reloaded")
    

asyncio.run(setup(bot))
bot.run(token)

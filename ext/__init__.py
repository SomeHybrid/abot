import discord

from .logger import logger as logging
from .db import initialize


async def setup(bot: discord.Bot):
    for extension in ("combat", "eco", "auction"):
        try:
            bot.load_extension(f"ext.{extension}")
        except Exception as e:
            logging.error(f"Failed to load extension {extension}.", exc_info=e)
        else:
            logging.info(f"Loaded extension {extension}.")

    try:
        await db.initialize()
    except Exception as e:
        logging.error("Failed to migrate database.", exc_info=e)
    else:
        logging.info("Migrated database.")


def reload_cogs(bot: discord.Bot):
    bot.reload_extension("ext.eco")
    bot.reload_extension("ext.combat")
    bot.reload_extension("ext.auction")

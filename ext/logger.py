import logging

logging.basicConfig(level=logging.ERROR, format='[%(asctime)s] (%(levelname)s): %(name)s: %(message)s', datefmt='%y-%m-%d %H:%M:%S')

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

logging.getLogger("discord").setLevel(logging.WARNING)

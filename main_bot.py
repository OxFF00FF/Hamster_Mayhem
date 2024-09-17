import logging

from Src.Hamster_bot import HamsterUltimate
from Src.Login import hamster_client

if __name__ == '__main__':
    try:
        bot = HamsterUltimate(TOKEN=hamster_client())
        bot.run()

    except Exception as e:
        logging.error(e)


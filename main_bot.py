import logging

from Src.Hamster_ultimate import HamsterUltimate

if __name__ == '__main__':
    try:
        bot = HamsterUltimate()
        bot.run()

    except Exception as e:
        logging.error(e)

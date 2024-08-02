import logging
import os
from Src.utils import WHITE, RESET, banner
from Src.Hamster import HamsterKombatClicker

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s{RESET}", level=logging.INFO)

# --- CONFIG --- #

BOT_TOKEN = os.getenv('BOT_TOKEN_MY')
GROUP_ID = os.getenv('GROUP_ID_MY')
HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')

# --- CONFIG --- #


def main():
    hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)
    hamster_client.daily_info()


if __name__ == '__main__':
    print(banner)

    main()
    pass

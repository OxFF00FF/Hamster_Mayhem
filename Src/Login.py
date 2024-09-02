import logging
import os
from Src.db_SQlite import ConfigDB
from Src.Hamster import HamsterKombatClicker

config = ConfigDB()


def hamster_client():
    try:
        HAMSTER_TOKEN = os.getenv(config.account)
        return HamsterKombatClicker(HAMSTER_TOKEN)

    except Exception as e:
        logging.error(e)

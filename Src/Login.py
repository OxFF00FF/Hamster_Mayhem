import logging
import os
from Src.Hamster import HamsterKombatClicker
from Src.Settings import load_settings


def hamster_client():
    settings = load_settings()
    try:
        HAMSTER_TOKEN = os.getenv(settings['account'])
        return HamsterKombatClicker(HAMSTER_TOKEN)

    except Exception as e:
        logging.error(e)

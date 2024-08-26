import os
from Src.Hamster import HamsterKombatClicker
from Src.Settings import load_settings


def hamster_client():
    settings = load_settings()
    HAMSTER_TOKEN = os.getenv(settings['account'])
    return HamsterKombatClicker(HAMSTER_TOKEN)

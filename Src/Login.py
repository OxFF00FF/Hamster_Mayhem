import os
from Src.Hamster import HamsterKombatClicker
from Src.Settings import load_settings, save_settings


def hamster_client():
    try:
        settings = load_settings()
        HAMSTER_TOKEN = os.getenv(settings['account'])
        settings['hamster_token'] = True
        save_settings(settings)
        return HamsterKombatClicker(HAMSTER_TOKEN)

    except:
        return HamsterKombatClicker('HAMSTER_TOKEN_1')

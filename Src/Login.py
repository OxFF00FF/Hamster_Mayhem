import os

from Src.Hamster import HamsterKombatClicker
from Src.utils import load_settings

settings = load_settings()
HAMSTER_TOKEN = os.getenv(settings['account'])
hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)

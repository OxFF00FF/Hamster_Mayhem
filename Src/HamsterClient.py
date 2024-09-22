from Src.Hamster import HamsterKombatClicker
from config import app_config


client = HamsterKombatClicker(hamster_token=app_config.HAMSTER_TOKEN_1)
config = client.user_config

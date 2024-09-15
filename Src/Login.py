import logging
import os
import re

from Src.db_SQlite import ConfigDB
from Src.Hamster import HamsterKombatClicker

config = ConfigDB()


def hamster_client(account: str = None, token: str = None):
    try:
        if account is not None:
            if re.match(r'^HAMSTER_TOKEN_[1-9]$', account.strip()):
                config.account = account
                HAMSTER_TOKEN = os.getenv(config.account)
            else:
                print(f"Account `{account}` not found in .env file")
                exit(1)

        if token is not None and config.token is not None and config.token.strip() != "":
            if re.match(r'^Bearer [A-Za-z0-9]+$', token.strip()):
                config.token = token
                HAMSTER_TOKEN = config.token
            else:
                print(f"Token `{token}` is invalid")
                exit(1)

        else:
            logging.warning(f"Used `HAMSTER_TOKEN_1` from your .env file by default")
            HAMSTER_TOKEN = os.getenv(config.account)

        return HamsterKombatClicker(HAMSTER_TOKEN)
    except Exception as e:
        print(f"Error initializing HamsterKombatClicker: {e}")
        exit(1)

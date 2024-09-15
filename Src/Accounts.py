import logging
import os

from Src.Colors import *
from Src.Menu import main_menu
from Src.db_SQlite import ConfigDB
from Src.Hamster import HamsterKombatClicker
from Src.Login import hamster_client
from Src.utils import localized_text, kali

config = ConfigDB()


def choose_account():
    accounts = [{'key': key, 'token': value} for key, value in os.environ.items() if key.startswith('HAMSTER')]
    current_account = hamster_client().get_account_info()

    if len(accounts) > 1:
        print(f"{localized_text('detected_accounts')} {len(accounts)}: ")
        account_dict = {}

        for e, account in enumerate(accounts):
            token = account['token']
            key = account['key']

            try:
                hamster = HamsterKombatClicker(token)
                account_info = hamster.get_account_info()
                user_name = account_info.get('name', 'n/a')
                user_id = account_info.get('id', 'n/a')

                if user_name == current_account.get('name', 'n/a'):
                    print(f"[{e + 1}] · {LIGHT_BLUE}{user_name} ({user_id}){WHITE} ({localized_text('logged_in')})")
                else:
                    print(f"[{e + 1}] · {user_name} ({user_id})")
                account_dict[str(e + 1)] = token

            except Exception as e:
                print(f"[X] · {LIGHT_RED}{localized_text('error_dont_recieved_account_data', key)}{WHITE}")
                logging.error(e)

        accounts_numbers = '/'.join([f"{e + 1}" for e in range(len(accounts))])
        account_choice = input(kali(f"{accounts_numbers}/0", '~/Accounts', localized_text('choose_account')))
        if account_choice.isdigit() and int(account_choice) <= len(accounts):
            return f"HAMSTER_TOKEN_{account_choice}" if account_choice in account_dict else "HAMSTER_TOKEN_1"

        elif account_choice == '0':
            main_menu()

    else:
        print(localized_text('one_account_detected'))
        return "HAMSTER_TOKEN_1"

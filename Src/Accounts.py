import os

from dotenv import load_dotenv

from Src.Colors import *
from Src.Hamster import HamsterKombatClicker
from Src.Menu import main_menu
from Src.utils import localized_text, kali, line_after
from Src.HamsterClient import client, config
from Src.Api.Endpoints import HamsterEndpoints


def choose_account():
    load_dotenv()
    accounts = [{'key': key, 'token': value} for key, value in os.environ.items() if key.startswith('HAMSTER')]
    current_account = HamsterEndpoints.get_account_info(client.headers)

    if len(accounts) > 1:
        print(f"{localized_text('detected_accounts')} {len(accounts)}: ")
        account_dict = {}

        for e, account in enumerate(accounts):
            token = account['token']
            key = account['key']

            try:
                hamster = HamsterKombatClicker(token)
                account_info = HamsterEndpoints.get_account_info(hamster.headers)
                user_name = account_info.name
                user_id = account_info.id

                if user_name == current_account.name:
                    print(f"[{e + 1}] · {LIGHT_BLUE}{user_name} [{user_id}]{WHITE} ({localized_text('logged_in')})")
                else:
                    print(f"[{e + 1}] · {user_name} [{user_id}]")
                account_dict[str(e + 1)] = token

            except:
                print(f"[X] · {LIGHT_RED}{localized_text('error_dont_recieved_account_data', key)}{WHITE}")

        print(f"[0] · Остатьтся в текущем аккаунте (Выйти в главное меню)\n")
        accounts_numbers = '/'.join([f"{e + 1}" for e in range(len(accounts))])
        account_choice = input(kali(f"{accounts_numbers}/0", '~/Accounts', localized_text('choose_account')))
        if account_choice == '0':
            main_menu()
            return config.account

        elif int(account_choice) <= len(accounts):
            return f"HAMSTER_TOKEN_{account_choice}" if account_choice in account_dict else "HAMSTER_TOKEN_1"

    else:
        print(f"ℹ️  {localized_text('one_account_detected')}")
        line_after(blank_line=False)
        return "HAMSTER_TOKEN_1"

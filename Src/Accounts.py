import os
import sys

from dotenv import load_dotenv

from Src.Colors import *
from Src.Hamster import HamsterKombatClicker
from Src.Menu import main_menu
from Src.utils import localized_text, kali, line_after
from Src.HamsterClient import client
from Src.Api.Endpoints import HamsterEndpoints


def choose_account():
    load_dotenv()

    accounts = [{'key': key, 'token': value} for key, value in os.environ.items() if key.startswith('HAMSTER')]
    current_account = HamsterEndpoints.get_account_info(client.headers)

    unique_accounts = set()
    if len(accounts) > 1:
        print(f"{localized_text('detected_accounts')} {len(accounts)}: ")
        account_dict = {}

        for e, account in enumerate(accounts):
            token = account['token']
            key = account['key']

            if token not in unique_accounts:
                unique_accounts.add(token)
                try:
                    hamster = HamsterKombatClicker(token)
                    account_info = HamsterEndpoints.get_account_info(hamster.headers)
                    if account_info.name == current_account.name:
                        print(f"[{e + 1}] · {LIGHT_BLUE}{account_info.name} [{account_info.id}]{WHITE} ({localized_text('logged_in')})")
                    else:
                        print(f"[{e + 1}] · {account_info.name} [{account_info.id}]")
                    account_dict[str(e + 1)] = token

                except Exception as ex:
                    print(f"[X] · {LIGHT_RED}{localized_text('error_dont_recieved_account_data', key)}: {ex}{WHITE}")

        print(localized_text('stay_in_current_account'))
        accounts_numbers = '/'.join([f"{e + 1}" for e in range(len(account_dict))])  # Измените здесь
        account_choice = input(kali(f"{accounts_numbers}/0", '~/Accounts', localized_text('choose_account')))
        if account_choice in account_dict:
            os.environ['SELECTED'] = account_dict[account_choice]

            selected_account = f"HAMSTER_TOKEN_{account_choice}"
            print(f"Restarting with {selected_account}...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        if account_choice == '0':
            main_menu()
            return

    else:
        print(f"ℹ️  {localized_text('one_account_detected')}")
        line_after(blank_line=False)
        return "HAMSTER_TOKEN_1"

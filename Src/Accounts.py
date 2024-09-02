import os

from Src.Colors import *
from Src.Hamster import HamsterKombatClicker
from Src.Login import hamster_client
from Src.utils import line_after


def choose_account():
    accounts = [{'key': key, 'token': value} for key, value in os.environ.items() if key.startswith('HAMSTER')]
    current_account = hamster_client().get_account_info()

    if len(accounts) > 1:
        print(f"Обнаружено аккаунтов {len(accounts)}: ")
        account_dict = {}

        for e, account in enumerate(accounts):
            token = account['token']
            key = account['key']

            try:
                hamster = HamsterKombatClicker(token)
                account_info = hamster.get_account_info()
                username = account_info.get('username', 'n/a')
                first_name = account_info.get('firstName', 'n/a')
                last_name = account_info.get('lastName', 'n/a')

                if username == current_account.get('username', 'n/a'):
                    print(f"[{e + 1}] · {LIGHT_BLUE}{first_name} {last_name} ({username}){WHITE} (вход выполнен)")
                else:
                    print(f"[{e + 1}] · {first_name} {last_name} ({username})")

                account_dict[str(e + 1)] = token
            except Exception:
                print(f"[X] · {LIGHT_RED}Не удалось получить данные аккаунта для `{key}`. Неверно указан токен{WHITE}")

        account_choice = input(f"\n{DARK_GRAY}Какой аккаунт хотите использовать?{WHITE}\n{CYAN}Выберите номер: {WHITE}")
        line_after()
        return f"HAMSTER_TOKEN_{account_choice}" if account_choice in account_dict else None
    else:
        print(f"Обнаружен только 1 аккаунт в вашем .env файле. Используется `HAMSTER_TOKEN_1`")
        return "HAMSTER_TOKEN_1"

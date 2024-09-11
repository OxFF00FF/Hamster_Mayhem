import asyncio
import re

from spinners import Spinners

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Accounts import choose_account
from Src.Generators import genetare_for_all_games, generate_for_game
from Src.Login import hamster_client
from Src.Menu import main_menu, playground_menu, minigames_menu, settings_menu, main_menu_not_logged
from Src.utils import line_after, line_before, get_games_data, spinners_table, localized_text, kali

config = ConfigDB()


def handle_main_menu_choice(choice):
    if choice == '#':
        line_before()
        print(hamster_client().daily_info())

    elif choice == '1':
        line_before()
        hamster_client().complete_taps()

    elif choice == '2':
        line_before()
        hamster_client().complete_daily_tasks()

    elif choice == '3':
        line_before()
        hamster_client().complete_daily_chipher()

    elif choice == '4':
        line_before()
        upgrades_info = hamster_client()._collect_upgrades_info()
        if all(card['available'] for card in upgrades_info['cards']):
            hamster_client().complete_daily_combo()
        else:
            choice = input(f"{localized_text('not_all_cards_available_today')}\n{CYAN}▶️  {localized_text('yes_enter')}: {WHITE}")
            if str(choice.lower()) == 'y'.lower():
                hamster_client().complete_daily_combo(buy_anyway=True)

    elif choice == '5':
        line_before()
        handle_minigames_choice()

    elif choice == '6':
        handle_playground_menu_choice()

    elif choice == 's':
        handle_settings_menu_choice()

    elif choice == 'a':
        line_before()
        config.account = choose_account()

        line_before()
        hamster_client().login()

    elif choice == '$':
        line_before()
        cards = hamster_client().get_most_profitable_cards()
        print(localized_text('info_rent_coeff_coefficient'))

        print(localized_text('top_profit_cards'))
        for e, card in enumerate(cards):
            price = f"{LIGHT_YELLOW}{card['price']:,}{WHITE} · {LIGHT_MAGENTA}+{card['profitPerHour']:,}{WHITE} {localized_text('per_hour')} · {MAGENTA}+{card['profitPerHourDelta']:,}{WHITE} {localized_text('per_hour_after_buy')}".replace(',', ' ')
            print(
                f"#   {e + 1}. {GREEN}{card['name']}{WHITE} ({card['id']}) · {card['section']}\n"
                f"💰  {YELLOW}{localized_text('price')}: {price}\n"
                f"🕞  {YELLOW}{localized_text('payback_time')}: {LIGHT_GREEN}{card['payback_period']}{WHITE} (~{card['payback_days']} {localized_text('days')}) \n"
                f"📊  {YELLOW}{localized_text('profitability_ratio')}: {LIGHT_CYAN}{card['profitability_ratio']:.4f}%{WHITE}"
            )
            if e < len(cards) - 1:
                print("-" * 30)

    elif choice.startswith('$'):
        line_before()
        cards = hamster_client().get_most_profitable_cards()
        card_index = int(choice[1:]) - 1

        if 0 <= card_index < len(cards):
            card = cards[card_index]
            upgrade_id = card['id']
            hamster_client()._buy_upgrade(upgradeId=upgrade_id)
            hamster_client().get_most_profitable_cards()

    elif choice.startswith('+'):
        line_before()
        match = re.search(pattern=r'\+(.*?)$', string=choice)
        if match:
            upgrade_id = match.group(1)
            hamster_client()._buy_upgrade(upgradeId=upgrade_id)

    elif choice == 'm':
        line_before()
        main_menu()

    elif choice == '0':
        line_before()
        print(f"ℹ️  {localized_text('exit')}")
        line_after()
        exit(1)

    else:
        line_before()
        print(f"ℹ️  {localized_text('no_such_option')}")


def handle_main_menu_not_logged_choice(choice):
    if choice == '6':
        handle_playground_menu_choice()

    elif choice == 'm':
        line_before()
        main_menu_not_logged()

    elif choice == '0':
        line_before()
        print(f"ℹ️  {localized_text('exit')}")
        line_after()
        exit(1)

    else:
        line_before()
        print(f"ℹ️  {localized_text('no_such_option')}")


def handle_playground_menu_choice():
    games_data = [app for app in get_games_data()['apps'] if app.get('available')]
    games_prefix = {str(index + 1): game['prefix'] for index, game in enumerate(games_data)}
    games = [str(i + 1) for i in range(len(games_data))]
    line_before()

    while True:
        playground_menu()
        # choice = input(f"{DARK_GRAY}{localized_text('choose_action')}\n{CYAN}▶️  (1/2/3/4/5/6/7/8/9/*/</0): {RESET}")
        choice = input(kali(f"{'/'.join(games)}/</0"))

        line_before()

        if choice in games_prefix:
            generate_for_game(games_prefix[choice])

        elif choice.startswith('*'):
            if choice.strip('*') == '':
                asyncio.run(genetare_for_all_games())

            else:
                games_count = int(choice.strip('*'))
                asyncio.run(genetare_for_all_games(games_count))

        elif choice == '<':
            print(f"ℹ️  {localized_text('reached_main_menu')}")
            return

        elif choice == '0':
            print(f"ℹ️  {localized_text('exit')}")
            line_after()
            exit(1)

        else:
            print(f"ℹ️  {localized_text('no_such_option')}")
            line_after()


def handle_minigames_choice():
    minigames = get_games_data()['minigames']

    while True:
        minigames_menu()
        choices = [str(i + 1) for i in range(len(minigames))]
        # choice = input(f"{DARK_GRAY}{localized_text('choose_action')}\n{CYAN}▶️  ({'/'.join(choices)}/</0): {RESET}")
        choice = input(kali(f"{'/'.join(choices)}/</0"))
        line_before()

        if choice in choices:
            selected_index = int(choice) - 1
            hamster_client().complete_daily_minigame(minigames[selected_index]['title'])
            line_after()

        elif choice == '<':
            print(f"ℹ️  {localized_text('reached_main_menu')}")
            return

        elif choice == '0':
            print(f"ℹ️  {localized_text('exit')}")
            line_after()
            exit(1)

        else:
            print(f"ℹ️  {localized_text('no_such_option')}")
            line_after()


def handle_settings_menu_choice():
    line_before()

    while True:
        settings_menu()
        # choice = input(f"{DARK_GRAY}{localized_text('choose_action')}\n{CYAN}▶️  (1/2/3/4/5/</0): {RESET}")
        choice = input(kali('1/2/3/4/5/</0'))
        line_before()

        if choice == '1':
            if config.lang == 'ru':
                config.lang = 'en'

            elif config.lang == 'en':
                config.lang = 'ru'

            print(f"ℹ️  {localized_text('change_lang')}")
            line_after()

        elif choice == '2':
            config.send_to_group = not config.send_to_group
            status = f"{GREEN}{localized_text('on')}а{WHITE}" if config.send_to_group else f"{RED}{localized_text('off')}а{WHITE}"
            print(f"{localized_text('info_send_promo_to_group')} {status}")
            line_after()

        elif choice == '3':
            config.apply_promo = not config.apply_promo
            status = f"{GREEN}{localized_text('on')}о{WHITE}" if config.apply_promo else f"{RED}{localized_text('off')}о{WHITE}"
            print(f"{localized_text('info_apply_promo')} {status}")
            line_after()

        elif choice == '4':
            config.save_to_file = not config.save_to_file
            status = f"{GREEN}{localized_text('on')}о{WHITE}" if config.apply_promo else f"{RED}{localized_text('off')}о{WHITE}"
            print(f"{localized_text('info_save_to_file')} {status}")
            line_after()

        elif choice.startswith('5'):
            config.balance_threshold = choice.split('_')[-1]

        elif choice == 'default':
            config.spinner = 'default'
            print(f"ℹ️  {localized_text('info_default_spinner')}")
            line_after()

        elif choice == 'hamster':
            config.spinner = 'hamster'
            print(f"ℹ️  {localized_text('info_default_spinner')}")
            line_after()

        elif choice == 'list':
            print(localized_text('spinners_list'))
            print(spinners_table())
            line_after()

        elif choice.startswith('spinner'):
            spinner_number = int(choice.split('_')[-1]) - 1
            spinner_name = list(Spinners)[spinner_number].name
            config.spinner = spinner_name
            print(f"ℹ️  {localized_text('info_spinner_changed_to')} `{spinner_name}`")
            line_after()


        elif choice == '<':
            print(f"ℹ️  {localized_text('reached_main_menu')}")
            return

        elif choice == '0':
            print(f"ℹ️  {localized_text('exit')}")
            line_after()
            exit(1)

        else:
            print(f"ℹ️  {localized_text('no_such_option')}")
            line_after()

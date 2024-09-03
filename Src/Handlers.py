import asyncio
import re

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Accounts import choose_account
from Src.Generators import genetare_for_all_games, generate_for_game
from Src.Login import hamster_client
from Src.Menu import main_menu, playground_menu, minigames_menu, settings_menu
from Src.utils import line_after, line_before, get_games_data, spinners_table, localized_text

config = ConfigDB()
lang = config.lang


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
            choice = input(f"Сегодня не все карты доступны!\nХотите купить только доступные? Y(да) / Enter(нет): ")
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
        top_10_cards = hamster_client().evaluate_cards()
        print(f"Коэффициент рентабельности означает, что за каждую потраченную монету вы получите\n"
              f"прирост прибыль в размере указанного % от суммы, потраченной на покупку этой карточки.\n")

        print(f"Топ 20 самых выгодных карт (показаны только доступные для покупки): \n")
        for card in top_10_cards:
            price = f"{LIGHT_YELLOW}{card['price']:,}{WHITE} · {LIGHT_MAGENTA}+{card['profitPerHour']:,}{WHITE} в час · {MAGENTA}+{card['profitPerHourDelta']:,}{WHITE} в час (после покупки)".replace(',', ' ')
            print(
                f"🏷  {GREEN}{card['name']}{WHITE} ({card['id']}) · {card['section']}\n"
                f"💰  {YELLOW}Стоимость: {price}\n"
                f"🕞  {YELLOW}Время окупаемости: {LIGHT_GREEN}{card['payback_period']}{WHITE} (~{card['payback_days']} дней) \n"
                f"📊  {YELLOW}Коэффициент рентабельности: {LIGHT_CYAN}{card['profitability_ratio']:.4f}%{WHITE}"
            )
            print("-" * 30)

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
        print(localized_text('exit'))
        line_after()
        exit(1)

    else:
        line_before()
        print(localized_text('no_such_option'))


def handle_playground_menu_choice():
    games_data = get_games_data()['apps']
    games_prefix = {str(index + 1): game['prefix'] for index, game in enumerate(games_data)}
    line_before()

    while True:
        playground_menu()
        choice = input(f"{DARK_GRAY}{localized_text('choose_action')}:\n{CYAN}(1/2/3/4/5/6/7/8/9/*/</0): {RESET}")
        line_before()

        if choice in games_prefix:
            generate_for_game(games_prefix[choice])
            line_after()

        elif choice == '*':
            asyncio.run(genetare_for_all_games())
            line_after()

        elif choice == '<':
            print('Вы вышли в главное меню')
            return

        elif choice == '0':
            print("Выход")
            line_after()
            exit(1)

        else:
            print("Такой опции нет")
            line_after()


def handle_minigames_choice():
    minigames = get_games_data()['minigames']

    while True:
        minigames_menu()
        choices = [str(i + 1) for i in range(len(minigames))]
        choice = input(f"{DARK_GRAY}{localized_text('choose_action')}:\n{CYAN}({'/'.join(choices)}/</0): {RESET}")
        line_before()

        if choice in choices:
            selected_index = int(choice) - 1
            hamster_client().complete_daily_minigame(minigames[selected_index]['title'])
            line_after()

        elif choice == '<':
            print('Вы вышли в главное меню')
            return

        elif choice == '0':
            print("Выход")
            line_after()
            exit(1)

        else:
            print("Такой опции нет")
            line_after()


def handle_settings_menu_choice():
    line_before()

    while True:
        settings_menu()
        choice = input(f"{DARK_GRAY}{localized_text('choose_action')}:\n{CYAN}(1/2/3/4/</0): {RESET}")
        line_before()

        if choice == '1':
            config.send_to_group = not config.send_to_group
            status = f'{GREEN}включена{WHITE}' if config.send_to_group else f'{RED}отключена{WHITE}'
            print(f'Отправка промокодов в группу {status}')
            line_after()

        elif choice == '2':
            config.apply_promo = not config.apply_promo
            status = f'{GREEN}включено{WHITE}' if config.apply_promo else f'{RED}отключено{WHITE}'
            print(f'Применение промокодов по умолчанию {status}')
            line_after()

        elif choice == '3':
            config.save_to_file = not config.save_to_file
            status = f'{GREEN}включено{WHITE}' if config.save_to_file else f'{RED}отключено{WHITE}'
            print(f'Сохранение в файл {status}')
            line_after()

        elif choice == '4':
            if config.lang == 'ru':
                config.lang = 'en'

            elif config.lang == 'en':
                config.lang = 'ru'

            print(localized_text('change_lang'))
            line_after()

        elif choice.startswith('spinner'):
            spinner_name = choice.split('_')[-1]
            if spinner_name == 'list':
                print(f"\nСписок доступных индикаторов загрузки")
                print(spinners_table())

            elif spinner_name == 'default':
                config.spinner = 'default'
                print(f"Индикатор загрузки установлен по умолчанию")

            else:
                config.spinner = spinner_name
                print(f"Индикатор загрузки изменен на `{spinner_name}`")
            line_after()

        elif choice == '<':
            print('Вы вышли в главное меню')
            return

        elif choice == '0':
            print("Выход")
            line_after()
            exit(1)

        else:
            print("Такой опции нет")
            line_after()

import asyncio
import re

from Src.Colors import *
from Src.Accounts import choose_account
from Src.Generators import genetare_for_all_games, generate_for_game
from Src.Login import hamster_client
from Src.Menu import main_menu, playground_menu
from Src.Settings import load_settings, save_settings
from Src.utils import line_after, line_before, get_games_data

settings = load_settings()


def handle_main_menu_choice(choice):
    if choice == '#':
        line_after()
        print(hamster_client().daily_info())

    elif choice == '1':
        line_after()
        hamster_client().complete_taps()

    elif choice == '2':
        line_after()
        hamster_client().complete_daily_tasks()

    elif choice == '3':
        line_after()
        hamster_client().complete_daily_chipher()

    elif choice == '4':
        line_after()
        hamster_client().complete_daily_minigame()

    elif choice == '5':
        line_after()
        upgrades_info = hamster_client()._collect_upgrades_info()
        if all(card['available'] for card in upgrades_info['cards']):
            hamster_client().complete_daily_combo()
        else:
            choice = input(f"Сегодня не все карты доступны!\nХотите купить только доступные? Y(да) / Enter(нет): ")
            if str(choice.lower()) == 'y'.lower():
                hamster_client().complete_daily_combo(buy_anyway=True)

    elif choice == '6':
        handle_playground_menu_choice()

    elif choice == 'a':
        line_after()
        settings['account'] = choose_account()
        save_settings(settings)
        hamster_client().login()

    elif choice == '$':
        line_after()
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
        line_after()
        match = re.search(pattern=r'\+(.*?)$', string=choice)
        if match:
            upgrade_id = match.group(1)
            hamster_client()._buy_upgrade(upgradeId=upgrade_id)

    elif choice == 'm':
        line_after()
        main_menu()

    elif choice == '0':
        line_after()
        print("Выход")
        line_before()
        exit(1)

    elif choice == 'toggle_group':
        line_after()
        settings['send_to_group'] = not settings['send_to_group']
        save_settings(settings)
        status = 'включена' if settings['send_to_group'] else 'отключена'
        print(f'Отправка промокодов в группу {status}')
        line_before()
        main_menu()

    elif choice == 'toggle_file':
        line_after()
        settings['save_to_file'] = not settings['save_to_file']
        save_settings(settings)
        status = 'включено' if settings['save_to_file'] else 'отключено'
        print(f'Сохранение в файл {status}')
        line_before()
        main_menu()

    elif choice == 'toggle_apply':
        line_after()
        settings['apply_promo'] = not settings['apply_promo']
        status = 'включено' if settings['apply_promo'] else 'отключено'
        save_settings(settings)
        print(f'Применение промокодов по умолчанию {status}')
        line_before()
        main_menu()

    else:
        line_after()
        print("Такой опции нет")


def handle_playground_menu_choice():
    games_data = get_games_data()['apps']
    games_prefix = {str(index + 1): game['prefix'] for index, game in enumerate(games_data)}

    while True:
        playground_menu()
        choice = input(f"\nВыберите действие\n{CYAN}(1/2/3/4/5/6/7/8/9/*/</0): {RESET}")
        line_after()

        if choice in games_prefix:
            generate_for_game(games_prefix[choice])
        elif choice == '*':
            asyncio.run(genetare_for_all_games())
            line_before()
        elif choice == '<':
            print('Вы вышли в главное меню')
            return
        elif choice == '0':
            print("Выход")
            line_before()
            exit(1)
        else:
            print("Такой опции нет")
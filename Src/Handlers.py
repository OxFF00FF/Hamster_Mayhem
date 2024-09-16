import asyncio
import re

from spinners import Spinners

from Src.Colors import *
from Src.Hamster_bot import HamsterUltimate
from Src.db_SQlite import ConfigDB
from Src.Accounts import choose_account
from Src.Generators import genetare_for_all_games, generate_for_game
from Src.Login import hamster_client
from Src.Menu import main_menu, playground_menu, minigames_menu, settings_menu, main_menu_not_logged
from Src.utils import line_after, line_before, get_games_data, spinners_table, localized_text, kali, remain_time

config = ConfigDB()


def handle_main_menu_choice(choice):
    if choice == '#':
        line_before()
        print(hamster_client().daily_info())

    elif choice == '@':
        bot = HamsterUltimate(TOKEN=hamster_client().HAMSTER_TOKEN)
        bot.run()

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
        hamster_client().complete_daily_combo()

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
        profitable_cards = hamster_client().get_most_profitable_cards()
        print(localized_text('info_rent_coeff_coefficient'))

        print(localized_text('top_profit_cards'))
        for e, card in enumerate(profitable_cards):
            remain = card['remain']
            expired_at = card['expired_at']

            if remain == 0:
                card_name = f"{GREEN}{card['name']}{WHITE}"
            else:
                card_name = f"{LIGHT_RED}{card['name']}{WHITE}"

            price = f"{LIGHT_YELLOW}{card['price']:,}{WHITE} · " \
                    f"{LIGHT_MAGENTA}+{card['profitPerHour']:,}{WHITE} {localized_text('per_hour')} · " \
                    f"{MAGENTA}+{card['profitPerHourDelta']:,}{WHITE} {localized_text('per_hour_after_buy')}".replace(',', ' ')

            text = f"#️⃣  {e + 1}. {card_name} · {card['level']} level\n" \
                   f"💰  {YELLOW}{localized_text('price')}: {price}\n" \
                   f"🕞  {YELLOW}{localized_text('payback_time')}: {LIGHT_GREEN}{card['payback_period']}{WHITE} (~{card['payback_days']} {localized_text('days')}) \n" \
                   f"📊  {YELLOW}{localized_text('profitability_ratio')}: {LIGHT_CYAN}{card['profitability_ratio']:.4f}%{WHITE}"

            if remain != 0:
                text += f"\n\n🔄  {YELLOW}Будет доступна через: {LIGHT_GREEN}{remain_time(remain)}{WHITE}"

            if expired_at:
                text += f"\n📅  {YELLOW}Осталось:{WHITE} {LIGHT_GREEN}{expired_at}{WHITE}"

            print(text)
            if e < len(profitable_cards) - 1:
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
        choice = input(kali(f"{'/'.join(games)}/</0", '~/Playground', localized_text('choose_action')))

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
        choice = input(kali(f"{'/'.join(choices)}/</0", '~/Minigames', localized_text('choose_action')))
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
        choice = input(kali('1/2/3/4/5/6/7/8/9/l/g/a/f</0', '~/Settings', localized_text('choose_action')))
        line_before()

        if choice.startswith('1'):
            config.balance_threshold = choice.split('_')[-1]

        elif choice == '2':
            config.complete_taps = not config.complete_taps

        elif choice == '3':
            config.complete_tasks = not config.complete_tasks

        elif choice == '4':
            config.complete_cipher = not config.complete_cipher

        elif choice == '5':
            config.complete_minigames = not config.complete_minigames

        elif choice == '6':
            config.complete_combo = not config.complete_combo

        elif choice == '7':
            config.complete_autobuy_upgrades = not config.complete_autobuy_upgrades

        elif choice == '8':
            config.complete_promocodes = not config.complete_promocodes

        elif choice == 's':
            config.all_cards_in_top = not config.all_cards_in_top

        elif choice == 't':
            if config.cards_in_top == 10:
                config.cards_in_top = 5
            else:
                if config.cards_in_top == 5:
                    config.cards_in_top = 10

        elif choice == 'l':
            if config.lang == 'ru':
                config.lang = 'en'

            elif config.lang == 'en':
                config.lang = 'ru'

            print(f"ℹ️  {localized_text('change_lang')}")
            line_after()

        elif choice == 'g':
            config.send_to_group = not config.send_to_group
            status = f"{GREEN}{localized_text('on')}а{WHITE}" if config.send_to_group else f"{RED}{localized_text('off')}а{WHITE}"
            print(f"{localized_text('info_send_promo_to_group')} {status}")
            line_after()

        elif choice == 'a':
            config.apply_promo = not config.apply_promo
            status = f"{GREEN}{localized_text('on')}о{WHITE}" if config.apply_promo else f"{RED}{localized_text('off')}о{WHITE}"
            print(f"{localized_text('info_apply_promo')} {status}")
            line_after()

        elif choice == 'f':
            config.save_to_file = not config.save_to_file
            status = f"{GREEN}{localized_text('on')}о{WHITE}" if config.apply_promo else f"{RED}{localized_text('off')}о{WHITE}"
            print(f"{localized_text('info_save_to_file')} {status}")
            line_after()

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

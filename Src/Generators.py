import logging

import asyncio
import platform
from Src.utils import get_games_data, localized_text, kali
from Src.HamsterClient import client, config


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

choice_text = kali(localized_text('yes_enter'), '~/Playground', localized_text('apply_promo_after_generate'))


def generate_promocodes(prefix='', apply_promo=False):
    count = input(kali(localized_text('enter_one'), '~/Playground', localized_text('count_promocodes_to_generate')))
    if count == '':
        count = 1
        print(f"\n⚠️  {localized_text('count_not_specified')}\n")

    if int(count) <= 0:
        print(localized_text('error_count_must_great_0'))

    try:
        asyncio.run(client.get_promocodes(int(count), config.send_to_group, apply_promo, prefix, config.save_to_file, one_game=True))

    except Exception as e:
        logging.error(e)
        print(f"🚫  {localized_text('error_generate_failed')}")

    finally:
        pass


def generate_for_game(prefix):
    if config.has_hamster_token:
        if config.apply_promo:
            generate_promocodes(prefix=prefix, apply_promo=config.apply_promo)
        else:
            choice = input(choice_text)
            if choice.lower() == 'y':
                generate_promocodes(prefix=prefix, apply_promo=True)
            elif choice == '':
                generate_promocodes(prefix=prefix)
            else:
                print(f"ℹ️  {localized_text('no_such_option')}")
    else:
        generate_promocodes(prefix=prefix)


async def genetare_for_all_games():
    games_data = get_games_data()

    if config.has_hamster_token:
        choice = input(choice_text)
        apply_promo = str(choice.lower()) == 'y'.lower()

    count = input(kali(localized_text('enter_one'), '~/Generate for all', localized_text('count_promocodes_to_generate_all_games')))
    if count == '':
        count = 1
        print(f"\n⚠️  {localized_text('count_not_specified')}")

    if int(count) <= 0:
        print(localized_text('error_count_must_great_0'))
        exit(1)

    tasks = [client.get_promocodes(int(count), config.send_to_group, apply_promo, app["prefix"], config.save_to_file, one_game=False) for app in games_data]
    await asyncio.gather(*tasks)


async def generate_for_available_games(task_count):
    games, remain = client.minigames_for_generate()
    limited_games_data = games[:task_count]

    tasks = [client.get_promocodes(int(game['count']), False, True, game["prefix"], False, one_game=True) for game in limited_games_data]
    await asyncio.gather(*tasks)

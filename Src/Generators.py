import logging

import asyncio

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Login import hamster_client
from Src.utils import get_games_data, localized_text

config = ConfigDB()

choice_text = f"{DARK_GRAY}{localized_text('apply_promo_after_generate')}{CYAN}\n{localized_text('yes_enter')}: "


def generate_promocodes(prefix='', apply_promo=False):
    count = input(f"\n{DARK_GRAY}{localized_text('count_promocodes_to_generate')}{CYAN}\n{localized_text('enter_one')}: {WHITE}")
    if count == '':
        count = 1
        print(f"\n⚠️  {localized_text('count_not_specified')}")

    if int(count) <= 0:
        print(localized_text('error_count_must_great_0'))

    try:
        asyncio.run(hamster_client().get_promocodes(int(count), config.send_to_group, apply_promo, prefix, config.save_to_file, config.spinner))

    except Exception as e:
        logging.error(e)
        print(f"🚫  {localized_text('error_generate_failed')}")

    finally:
        pass


def generate_for_game(prefix):
    if config.hamster_token:
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
    apps = get_games_data()['apps']

    if config.hamster_token:
        choice = input(choice_text)
        apply_promo = str(choice.lower()) == 'y'.lower()

    count = input(f"\n{DARK_GRAY}{localized_text('count_promocodes_to_generate_all_games')}{CYAN}\n{localized_text('enter_one')}: {WHITE}")
    if count == '':
        count = 1
        print(f"\n⚠️  {localized_text('count_not_specified')}")

    if int(count) <= 0:
        print(localized_text('error_count_must_great_0'))
        exit(1)

    tasks = [hamster_client().get_promocodes(int(count), config.send_to_group, apply_promo, app["prefix"], config.save_to_file) for app in apps]
    await asyncio.gather(*tasks)

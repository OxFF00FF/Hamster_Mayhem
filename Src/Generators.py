import asyncio
import logging

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Login import hamster_client
from Src.utils import get_games_data

config = ConfigDB()
lang = config.lang


def generate_promocodes(prefix='', apply_promo=False):
    count = input(f"\nКакое количество промокодов генерировать?\nEnter(по умолчанию 1): ")
    if count == '':
        count = 1
        print(f"⚠️  Количество промокодов не указано. Генерируется 1 по умолчанию")

    if int(count) <= 0:
        logging.error(f"\nКоличество должно быть числом больше 0")

    try:
        asyncio.run(hamster_client().get_promocodes(int(count), config.send_to_group, apply_promo, prefix, config.save_to_file, config.spinner))

    except Exception as e:
        logging.error(e)
        print(f"🚫  Произошла ошибка во время генерации. Попробуйте снова, если ошибки прололжаться, то попробуйте позже.")

    finally:
        pass


def generate_for_game(prefix):
    choice_text = f"\n{DARK_GRAY}Хотите применить промокоды после получения?{CYAN}\nY(да) / Enter(Нет): "
    if config.hamster_token:
        if config.apply_promo:
            generate_promocodes(prefix=prefix, apply_promo=config.apply_promo)
        else:
            choice = input(choice_text).lower()
            if choice == 'y':
                generate_promocodes(prefix=prefix, apply_promo=True)
            elif choice == '':
                generate_promocodes(prefix=prefix)
            else:
                print("Такой опции нет")
    else:
        generate_promocodes(prefix=prefix)


async def genetare_for_all_games():
    apps = get_games_data()['apps']

    if config.hamster_token:
        choice = input(f"\nХотите применить промокоды после получения?\nY(да) / Enter(Нет): ")
        apply_promo = str(choice.lower()) == 'y'.lower()

    count = input(f"\nКоличество промокодов для всех игр Enter(по умолчанию 1): ")
    if count == '':
        count = 1
        print("\nКоличество промокодов не предоставлено.\nГенерируется 1 по умолчанию")

    if int(count) <= 0:
        logging.error(f"\nКоличество должно быть числом больше 0")
        exit(1)

    tasks = [hamster_client().get_promocodes(int(count), config.send_to_group, apply_promo, app["prefix"], config.save_to_file) for app in apps]
    await asyncio.gather(*tasks)

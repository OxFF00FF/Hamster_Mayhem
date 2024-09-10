import os
import threading
import time
from datetime import datetime
from random import randint

from dotenv import load_dotenv

from Src.Colors import *
from Src.Login import hamster_client
from Src.db_SQlite import ConfigDB
from Src.utils import line_before, line_after, remain_time, localized_text

load_dotenv()
config = ConfigDB()

user = hamster_client().login().split()[-1].strip('(').strip(')')

print_lock = threading.Lock()


def random_delay():
    return randint(1000, 2000)


def current_time():
    print(f"{DARK_GRAY}⚙️  {datetime.now()} · {user}{WHITE}")


def process_taps():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_taps()
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_taps_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_cipher():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_daily_chipher()
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_cipher_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_tasks():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_daily_tasks()
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_tasks_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_balance():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().send_balance_to_group(update_time_sec=5000, chat_id=int(os.getenv('BOT_LOGS_GROUP_ID')))
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_balance_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_minigame_tiles():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_daily_minigame('tiles')
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_tiles_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_minigame_candles():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_daily_minigame('candles')
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_candles_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_combo():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            remain = hamster_client().complete_daily_combo(buy_anyway=True)
            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_combo_after')}: {remain_time(remain)}{WHITE}")

            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_autobuy_upgrades():
    while True:
        with print_lock:
            line_before(blank_line=False)
            current_time()

            most_profitable_cards = hamster_client().get_most_profitable_cards(top=3)
            for card in most_profitable_cards:
                hamster_client()._buy_upgrade(card)

            print(f"{LIGHT_YELLOW}⏳   {localized_text('next_purhase_after')}: {remain_time(random_delay())}{WHITE}")
            line_after(blank_line=False)
        time.sleep(random_delay())


def run_hamster_mayhem_ultimate():
    threads = [
        threading.Thread(target=process_balance),
        threading.Thread(target=process_taps),
        threading.Thread(target=process_tasks),
        threading.Thread(target=process_cipher),
        threading.Thread(target=process_combo),
        threading.Thread(target=process_minigame_tiles),
        threading.Thread(target=process_minigame_candles),
        threading.Thread(target=process_autobuy_upgrades),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


run_hamster_mayhem_ultimate()

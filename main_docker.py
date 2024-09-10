import os
import threading
import time
from datetime import datetime
from random import randint

from dotenv import load_dotenv

from Src.Login import hamster_client
from Src.utils import line_before, line_after, remain_time

load_dotenv()
user = hamster_client().login().split()[-1].strip('(').strip(')')

print_lock = threading.Lock()


def random_delay():
    return randint(1000, 2000)


def process_taps():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().complete_taps()
            print(f"⏳   Следующие тапы через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_cipher():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().complete_daily_chipher()
            print(f"⏳   Следующий шифр через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_tasks():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().complete_daily_tasks()
            print(f"⏳   Следующие задания через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_balance():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().send_balance_to_group(update_time_sec=5000, chat_id=int(os.getenv('BOT_LOGS_GROUP_ID')))
            print(f"⏳   Следующий баланс через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_minigame_tiles():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().complete_daily_minigame('tiles')
            print(f"⏳   Следующая игра Tiles через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


def process_minigame_candles():
    while True:
        with print_lock:
            line_before(blank_line=False)
            print(f"⚙️  {datetime.now()} · {user}")
            remain = hamster_client().complete_daily_minigame('candles')
            print(f"⏳   Следующая игра Candles через: {remain_time(remain)}")
            line_after(blank_line=False)
        time.sleep(remain + random_delay())


threads = [
    threading.Thread(target=process_minigame_tiles),
    threading.Thread(target=process_minigame_candles),
    threading.Thread(target=process_balance),
    threading.Thread(target=process_taps),
    threading.Thread(target=process_cipher),
    threading.Thread(target=process_tasks),
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

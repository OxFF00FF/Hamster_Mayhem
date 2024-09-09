import os
import threading
import time
from random import randint

from dotenv import load_dotenv

from Src.Login import hamster_client
from Src.utils import remain_time, line_before, line_after, countdown_timer

load_dotenv()
hamster_client().login()


def random_delay():
    return randint(1, 3600)


def process_taps():
    taps = hamster_client().get_cooldowns()['taps']
    while True:
        hamster_client().complete_taps()
        time.sleep(taps['remain'] + random_delay())


def process_cipher():
    cipher = hamster_client().get_cooldowns()['cipher']
    while True:
        hamster_client().complete_daily_chipher()
        time.sleep(cipher['remain'] + random_delay())


def process_tasks():
    tasks = hamster_client().get_cooldowns()['tasks']
    while True:
        hamster_client().complete_daily_chipher()
        time.sleep(tasks['remain'] + random_delay())


def process_balance():
    hamster_client().send_balance_to_group(chat_id=int(os.getenv('BOT_LOGS_GROUP_ID')))


threads = [
    threading.Thread(target=process_balance),
    threading.Thread(target=process_taps),
    threading.Thread(target=process_cipher),
    threading.Thread(target=process_tasks),
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

import asyncio
import os
import threading
import time

from dotenv import load_dotenv

from Src.Colors import *
from Src.Login import hamster_client
from Src.db_SQlite import ConfigDB
from Src.utils import line_before, line_after, remain_time, localized_text, current_time, random_delay

load_dotenv()
config = ConfigDB()
print_lock = threading.Lock()


class HamsterUltimate:

    def __init__(self, TOKEN: str):
        """
        :param TOKEN: Bearer token
        """
        self.Client = hamster_client(token=TOKEN).login(show_info=False).split()[-1].strip('(').strip(')')

        self.chat_id = os.getenv('BOT_LOGS_GROUP_ID')
        if self.chat_id is None:
            self.chat_id = os.getenv('CHAT_ID')

    def process_taps(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_taps:
                    remain = hamster_client().complete_taps()
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_taps_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(self.chat_id, message)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_taps_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_cipher(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_cipher:
                    remain = hamster_client().complete_daily_chipher()
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_cipher_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_cipher_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_tasks(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_tasks:
                    remain = hamster_client().complete_daily_tasks()
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_tasks_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_tasks_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_balance(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().send_balance_to_group(update_time_sec=5000, chat_id=int(self.chat_id))
                print(f"{LIGHT_YELLOW}⏳   {localized_text('next_balance_after')}: {remain_time(remain)}{WHITE}")

                line_after(blank_line=False)
            time.sleep(remain + random_delay())

    def process_minigame_tiles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_minigames:
                    remain = hamster_client().complete_daily_minigame('tiles')
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_minigames_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_minigame_candles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_minigames:
                    remain = hamster_client().complete_daily_minigame('candles')
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_minigames_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_combo(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_combo:
                    remain = hamster_client().complete_daily_combo(buy_anyway=True)
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_combo_after')}: {remain_time(remain)}{WHITE}"

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_combo_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_autobuy_upgrades(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_autobuy_upgrades:
                    remain = random_delay()
                    message = f"{LIGHT_YELLOW}⏳   {localized_text('next_purhase_after')}: {remain_time(remain)}{WHITE}"

                    most_profitable_cards = hamster_client().get_most_profitable_cards(top=5)
                    for card in most_profitable_cards:
                        hamster_client()._buy_upgrade(card)

                    print(message)
                    # hamster_client().send_to_chat(message, chat_id=self.chat_id)
                    time_to_sleep = remain

                else:
                    print(f"{YELLOW}⛔️  {localized_text('auto_upgrades_off')}{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep)
            else:
                return

    def process_keys_minigames(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_promocodes:
                    remain = hamster_client().get_keys_minigames_for_generate()
                    if isinstance(remain, list) and remain != []:
                        for game in remain:
                            asyncio.run(hamster_client().get_promocodes(count=int(game['count']), prefix=game['prefix'], apply_promo=True, one_game=True))

                            remain = random_delay() / 3
                            message = f"{LIGHT_YELLOW}⏳   {localized_text('next_keys_promocodes_after')}: {remain_time(remain)}{WHITE}"
                            print(message)
                            time.sleep(remain)
                            time_to_sleep = remain

                    else:
                        print(f"\n{LIGHT_YELLOW}⚠️  {localized_text('all_promocodes_recieved')}: {remain_time(remain)}{WHITE}")
                        time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  {localized_text('warning_auto_promocodes_off')}{WHITE}")
                    time_to_sleep = False

                if time_to_sleep:
                    print(f"\n{LIGHT_YELLOW}⚠️  {localized_text('all_promocodes_recieved')}: {remain_time(time_to_sleep)}{WHITE}")
                    time.sleep(time_to_sleep + random_delay())
                else:
                    return

                line_after(blank_line=False)

    def run(self):
        print('\nBot is running...\n')

        threads = [
            # threading.Thread(target=self.process_balance),
            # threading.Thread(target=self.process_taps),
            # threading.Thread(target=self.process_tasks),
            # threading.Thread(target=self.process_cipher),
            # threading.Thread(target=self.process_combo),
            # threading.Thread(target=self.process_minigame_tiles),
            # threading.Thread(target=self.process_minigame_candles),
            # threading.Thread(target=self.process_autobuy_upgrades),
            threading.Thread(target=self.process_keys_minigames),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

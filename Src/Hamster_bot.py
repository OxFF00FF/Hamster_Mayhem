import asyncio
import os
import threading
import keyboard
import time
from dotenv import load_dotenv

from Src.Colors import *
from Src.Login import hamster_client
from Src.db_SQlite import ConfigDB
from Src.utils import line_before, line_after, remain_time, localized_text, current_time, random_delay, get_games_data

load_dotenv()
config = ConfigDB()
print_lock = threading.Lock()


class HamsterUltimate:

    def __init__(self, TOKEN: str):
        """
        :param TOKEN: Bearer token
        """
        self.stop_event = threading.Event()
        self.Client = hamster_client(token=TOKEN).login(show_info=False).split()[-1].strip('(').strip(')')

    def process_taps(self):
        while not self.stop_event.is_set():
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_taps:
                    remain = hamster_client().complete_taps()
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_taps_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение тапов отключено{WHITE}")
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
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_cipher_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение шифра отключено{WHITE}")
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
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_tasks_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение заданий отключено{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_balance(self):
        while not self.stop_event.is_set():
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().send_balance_to_group(update_time_sec=5000, chat_id=int(os.getenv('BOT_LOGS_GROUP_ID')))
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
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_tiles_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение миниигр отключено{WHITE}")
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
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_minigame_candles_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение миниигр отключено{WHITE}")
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
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_combo_after')}: {remain_time(remain)}{WHITE}")
                    time_to_sleep = remain
                else:
                    print(f"{YELLOW}⛔️  Автоматическое прохождение комбо отключено{WHITE}")
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
                    most_profitable_cards = hamster_client().get_most_profitable_cards(top=3)
                    for card in most_profitable_cards:
                        hamster_client()._buy_upgrade(card)
                    print(f"{LIGHT_YELLOW}⏳   {localized_text('next_purhase_after')}: {remain_time(random_delay())}{WHITE}")
                    time_to_sleep = random_delay()
                else:
                    print(f"{YELLOW}⛔️  Автоматическая покупка карт отключена{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_keys_minigames(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                if config.complete_promocodes:
                    games_data = [app for app in get_games_data()['apps'] if app.get('available')]
                    promos = hamster_client()._get_promos()


                    for game in games_data:
                        promo = next((p for p in promos if p.get('name') == game.get('title')), None)

                        recieved_keys = promo.get('keys', 0) if promo else 0
                        keys_per_day = promo.get('per_day', 0) if promo else 1
                        is_claimed = promo['isClaimed'] if promo else False
                        prefix = game.get('prefix', '')
                        count = int(keys_per_day - recieved_keys)

                        if not is_claimed:
                            asyncio.run(hamster_client().get_promocodes(count=count, apply_promo=True, prefix=prefix, one_game=True))
                            break
                else:
                    print(f"{YELLOW}⛔️  Автоматическое получение промокодов отключено{WHITE}")
                    time_to_sleep = False

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return


    def run(self):
        print('\nBot is running...\nFor stop bot press Ctrl+C or press "q" key\n')

        threads = [
            threading.Thread(target=self.process_balance),
            threading.Thread(target=self.process_taps),
            threading.Thread(target=self.process_tasks),
            threading.Thread(target=self.process_cipher),
            threading.Thread(target=self.process_combo),
            threading.Thread(target=self.process_minigame_tiles),
            threading.Thread(target=self.process_minigame_candles),
            threading.Thread(target=self.process_autobuy_upgrades),
            threading.Thread(target=self.process_keys_minigames),
        ]

        def monitor_stop_key():
            keyboard.wait('q')
            self.stop_event.set()
            print("Bot was been stopped")
            exit(1)

        monitor_thread = threading.Thread(target=monitor_stop_key)
        monitor_thread.start()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        monitor_thread.join()

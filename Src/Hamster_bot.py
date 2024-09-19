import asyncio
import os
import threading
import time

from dotenv import load_dotenv

from Src.Colors import *
from Src.Login import hamster_client
from Src.db_SQlite import ConfigDB
from Src.utils import line_before, line_after, remain_time, localized_text, current_time, random_delay, check_environment, bot_start

load_dotenv()
config = ConfigDB()
print_lock = threading.Lock()


class HamsterUltimate:

    def __init__(self, TOKEN: str):
        """
        :param TOKEN: Bearer token
        """
        self.Client = hamster_client(token=TOKEN).login(show_info=False)

        check_environment(required=True)
        self.chat_id = os.getenv('BOT_LOGS_GROUP_ID')
        if self.chat_id is None:
            self.chat_id = os.getenv('CHAT_ID')

    def process_balance(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = 5000 + random_delay()

                message = f"🔄  {localized_text('next_balance_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                info = hamster_client()._get_balance()
                balance = f"✅  Баланс получен \n" \
                          f"💰  Баланс: {info['balanceCoins']:,} \n" \
                          f"🌟  Всего: {info['total']:,} \n" \
                          f"📈  Доход: {info['earn_per_hour']:,} в час\n" \
                          f"🔑  Ключей: {info['keys']:,} \n"
                hamster_client().send_to_chat(self.chat_id, message, balance.replace(',', ' '))
                line_after(blank_line=False)
            time.sleep(remain)

    def process_taps(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_taps() + random_delay()

                message = f"🔄  {localized_text('next_taps_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"👆  {localized_text('info_taps_completed')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_tasks(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_daily_tasks() + random_delay()

                message = f"🔄  {localized_text('next_tasks_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"📑  {localized_text('info_all_tasks_complete')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_cipher(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_daily_chipher() + random_delay()

                message = f"🔄  {localized_text('next_cipher_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"🔍  {localized_text('info_cipher_completed')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_combo(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_daily_combo(buy_anyway=True) + random_delay()

                message = f"🔄  {localized_text('next_combo_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"💰  {localized_text('info_combo_completed')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_minigame_tiles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_daily_minigame('tiles') + random_delay()

                message = f"🔄  {localized_text('next_minigame_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"🪙  {localized_text('info_minigame_complete'), 'Tiles'}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_minigame_candles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = hamster_client().complete_daily_minigame('candles') + random_delay()

                message = f"🔄  {localized_text('next_minigame_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"🔑  {localized_text('info_minigame_complete'), 'Candles'}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_autobuy_upgrades(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)

                remain = random_delay()

                message = f"🔄  {localized_text('next_purhase_after')}: {remain_time(remain)}"
                most_profitable_cards = hamster_client().get_most_profitable_cards(top=5)
                [hamster_client()._buy_upgrade(card) for card in most_profitable_cards]
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"🛍  {localized_text('upgrades_purhased')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def process_promocodes(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                games, remain = hamster_client().get_keys_minigames_for_generate()
                remain += random_delay()

                for game in games:
                    keys_count = int(game['count'])
                    promo_prefix = game['prefix']
                    asyncio.run(hamster_client().get_promocodes(count=keys_count, prefix=promo_prefix, apply_promo=True, one_game=True))
                    sleep_between_games = 1
                    message = f"🔄  {localized_text('next_keys_promocodes_after')}: {remain_time(sleep_between_games)}"
                    print(f"{LIGHT_YELLOW}{message}{WHITE}")
                    keys_recieved = localized_text('info_keys_recieved').split()[-1]
                    hamster_client().send_to_chat(self.chat_id, message, f"🎁  {promo_prefix} · {keys_recieved}: {keys_count}")
                    time.sleep(sleep_between_games)
                if games:
                    print(f"{GREEN}✅  {localized_text('all_promocodes_recieved')}{WHITE}")

                message = f"🔄  {localized_text('info_next_keys_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, f"🎉  {localized_text('all_promocodes_recieved')}")
                line_after(blank_line=False)
            time.sleep(remain)

    def run(self):
        bot_start()

        processes = [
            (True, self.process_balance, localized_text('auto_balance_off')),
            (config.complete_taps, self.process_taps, localized_text('warning_auto_taps_off')),
            (config.complete_tasks, self.process_tasks, localized_text('warning_auto_tasks_off')),
            (config.complete_cipher, self.process_cipher, localized_text('warning_auto_cipher_off')),
            (config.complete_combo, self.process_combo, localized_text('warning_auto_combo_off')),
            (config.complete_minigames, self.process_minigame_tiles, localized_text('warning_auto_minigames_off')),
            (config.complete_minigames, self.process_minigame_candles, localized_text('warning_auto_minigames_off')),
            (config.complete_autobuy_upgrades, self.process_autobuy_upgrades, localized_text('warning_auto_upgrades_off')),
            (config.complete_promocodes, self.process_promocodes, localized_text('warning_auto_promocodes_off')),
        ]

        threads = []

        for available, process, message in processes:
            if available:
                threads.append(threading.Thread(target=process))
            else:
                print(f"{YELLOW}⛔️  {message}{WHITE}")
        print()

        for thread in threads:
            thread.start()
            time.sleep(3)

        for thread in threads:
            thread.join()


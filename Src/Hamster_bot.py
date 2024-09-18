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
                time_to_sleep = remain

                line_after(blank_line=False)

            if time_to_sleep:
                time.sleep(time_to_sleep + random_delay())
            else:
                return

    def process_taps(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_taps()
                message = f"🔄   {localized_text('next_taps_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '👆  Тапы выполнены')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_cipher(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_daily_chipher()
                message = f"🔄   {localized_text('next_cipher_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '🔍  Шифр получен')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_tasks(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_daily_tasks()
                message = f"🔄   {localized_text('next_tasks_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '📑  Задания выполнены')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_minigame_tiles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_daily_minigame('tiles')
                message = f"🔄  {localized_text('next_minigame_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '🪙  Миниигра Tiles пройдена')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_minigame_candles(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_daily_minigame('candles')
                message = f"🔄  {localized_text('next_minigame_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '🔑  Миниигра Candles пройдена')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_combo(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().complete_daily_combo(buy_anyway=True)
                message = f"🔄   {localized_text('next_combo_after')}: {remain_time(remain)}"
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '💰  Комбо выполнено')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_autobuy_upgrades(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = random_delay()
                message = f"🔄   {localized_text('next_purhase_after')}: {remain_time(remain)}"
                most_profitable_cards = hamster_client().get_most_profitable_cards(top=5)
                [hamster_client()._buy_upgrade(card) for card in most_profitable_cards]
                print(f"{LIGHT_YELLOW}{message}{WHITE}")
                hamster_client().send_to_chat(self.chat_id, message, '🛍  Улучшения куплены')
                line_after(blank_line=False)

                time.sleep(remain + random_delay())

    def process_promocodes(self):
        while True:
            with print_lock:
                line_before(blank_line=False)
                current_time(self.Client)
                remain = hamster_client().get_keys_minigames_for_generate()
                if isinstance(remain, list) and remain != []:
                    for game in remain:
                        keys_count = int(game['count'])
                        promo_title = game['prefix']
                        asyncio.run(hamster_client().get_promocodes(count=keys_count, prefix=promo_title, apply_promo=True, one_game=True))

                        sleep_between_games = random_delay() / 3
                        message = f"🔄   {localized_text('next_keys_promocodes_after')}: {remain_time(sleep_between_games)}"

                        print(f"{LIGHT_YELLOW}{message}{WHITE}")
                        hamster_client().send_to_chat(self.chat_id, message, f'🎁  Получено {keys_count} промокодов для {promo_title}')
                        time.sleep(sleep_between_games)
                else:
                    print(f"\n{LIGHT_YELLOW}⚠️  {localized_text('all_promocodes_recieved')}: {remain_time(remain)}{WHITE}")
                    line_after(blank_line=False)

                    time.sleep(remain + random_delay())

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

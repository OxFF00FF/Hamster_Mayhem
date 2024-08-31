import asyncio
import base64
import datetime
import hashlib
import logging
import os
import random
import time
import traceback
import uuid
from datetime import datetime
from random import randint
from typing import Any

import aiohttp
import requests
from bs4 import BeautifulSoup as BS
from dotenv import load_dotenv
from fake_useragent import UserAgent
from fuzzywuzzy import fuzz

from Src.Colors import *
from Src.Settings import load_settings, save_settings, load_setting
from Src.utils import text_to_morse, remain_time, loading_v2, get_games_data, line_before, generation_status, get_salt, localized_text

load_dotenv()


class HamsterKombatClicker:

    def __init__(self, hamster_token, show_warning=False):
        """
        :param hamster_token: Ваш токен хомяка из браузерной версии игры
        """

        self.HAMSTER_TOKEN = hamster_token
        self.BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.GROUP_ID = os.getenv('GROUP_ID')
        self.GROUP_URL = os.getenv('GROUP_URL')

        self.base_url = 'https://api.hamsterkombatgame.io'

        if self.HAMSTER_TOKEN == 'XXX':
            logging.error(f'Отсутствует значение HAMSTER_TOKEN в вашем .env')
            exit(1)

        if show_warning:
            env = ['BOT_TOKEN', 'GROUP_ID', 'GROUP_URL']
            missing_values = [value for value in env if os.getenv(value) == 'XXX']
            if len(missing_values) > 0:
                logging.warning(f'{YELLOW}Следующие значения среды отсутствуют в вашем .env файле: {", ".join(missing_values)}{WHITE}')

    def _get_headers(self, hamster_token: str) -> dict:
        ua = UserAgent()
        return {
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://hamsterkombat.io',
            'Referer': 'https://hamsterkombat.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': ua.random,
            'accept': 'application/json',
            'authorization': hamster_token,
            'content-type': 'application/json',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def _get_telegram_user_id(self) -> str:
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()
            return response.json().get('clickerUser').get('id')

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _get_daily_combo(self) -> dict:
        try:
            response = requests.get('https://hamsterkombo.com/')
            response.raise_for_status()

            html = BS(response.content, 'html.parser')
            hamster_block = html.select('div[class="w-full flex flex-col gap-4"]')[0]
            combo_block = hamster_block.select('span[class="font-medium text-[12px] md:text-[16px] lg:font-semibold"]')[:3]
            date_block = hamster_block.select('span[class="text-center font-light opacity-70 mb-[16px]"]')

            date = f"{date_block[0].text.split(':')[-1].strip()} {datetime.today().year}"
            combo_from_site = [item.text.strip() for item in combo_block]
            logging.warning(f"⚙️  {combo_from_site}")
            combo_ids = []

            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            upgradesForBuy = response.json().get('upgradesForBuy')
            for upgrade in upgradesForBuy:
                for upgrade_name in combo_from_site:
                    name_from_site = str(upgrade_name.strip().lower())
                    name_from_hamster = str(upgrade.get('name').strip().lower())

                    match = fuzz.ratio(name_from_site, name_from_hamster)
                    if match > 85:
                        combo_ids.append(upgrade.get('id'))

            logging.warning(f"⚙️  {combo_ids}")
            return {'combo': combo_ids, 'date': date}

        except requests.exceptions.HTTPError as http_err:
            logging.error(http_err)

        except Exception as e:
            logging.error(e)

    def _get_daily_cipher(self) -> str:
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            encoded_cipher = response.json()['dailyCipher']['cipher']
            cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
            logging.warning(cipher)
            return cipher

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _get_balance(self) -> dict:
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clicker = response.json().get('clickerUser')
            return {
                'balanceCoins': int(clicker.get('balanceCoins')),
                'total': int(clicker.get('totalCoins')),
                'keys': int(clicker.get('balanceKeys')),
                'date': int(clicker.get('lastSyncUpdate'))
            }

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _activity_cooldowns(self) -> list:
        result = []
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            combo = response.json().get('dailyCombo', {})
            remain_combo = remain_time(combo.get('remainSeconds', 0))
            result.append({'combo': {'remain': remain_combo, 'isClaimed': combo.get('isClaimed', False)}})

            response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            config_data = response.json()
            cipher = config_data.get('dailyCipher', {})
            remain_cipher = remain_time(cipher.get('remainSeconds', 0))
            result.append({'cipher': {'remain': remain_cipher, 'isClaimed': cipher.get('isClaimed', False)}})

            response = requests.post('https://api.hamsterkombatgame.io/clicker/list-tasks', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            tasks = response.json().get('tasks', [])
            for task in tasks:
                if task.get('id') == 'streak_days':
                    remain_task = remain_time(task.get('remainSeconds', 0))
            result.append({'tasks': {'remain': remain_task, 'isClaimed': all(task.get('isCompleted', False) for task in tasks)}})

            response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clickerUser = response.json().get('clickerUser')
            availableTaps = int(clickerUser.get('availableTaps'))
            maxTaps = int(clickerUser.get('maxTaps'))
            tapsRecoverPerSec = int(clickerUser.get('tapsRecoverPerSec'))

            current_remain_time = int(availableTaps / tapsRecoverPerSec)
            total_remain_time = int(maxTaps / tapsRecoverPerSec)
            remain = remain_time(total_remain_time - current_remain_time)

            if availableTaps == maxTaps:
                result.append({'taps': {'remain': 'n/a', 'isClaimed': True}})
            else:
                result.append({'taps': {'remain': remain, 'isClaimed': False}})

            return result

        except requests.exceptions.HTTPError as http_err:
            logging.warning(f"🚫  HTTP ошибка: {http_err}")
            return result

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _get_promos(self) -> list:
        result = []
        try:
            response = requests.post(f'{self.base_url}/clicker/get-promos', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            promos = response.json().get('promos', [{}])
            states = response.json().get('states', [{}])

            for promo in promos:
                for state in states:
                    if promo['promoId'] == state['promoId']:
                        promo_name = promo['title']['en']
                        keys_today = state['receiveKeysToday']
                        remain_promo = remain_time(state['receiveKeysRefreshSec'])
                        is_claimed = True if keys_today == 4 else False
                        result.append({'remain': remain_promo, 'keys': keys_today, 'name': promo_name, 'isClaimed': is_claimed})
            return result

        except:
            return result

    def _get_minigames(self) -> list:
        result = []
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            games = response.json().get('dailyKeysMiniGames', [{}])
            for game in games.values():
                result.append(game)
            return result

        except:
            return result

    def _get_mini_game_cipher(self, mini_game: dict, one_point=False) -> str:
        minigame_cipher = ''
        try:
            if one_point:
                max_points = 1
            else:
                max_points = mini_game.get('maxPoints', 0)

            mini_game_id = mini_game.get('id')
            start_date = mini_game.get('startDate')
            user_id = self._get_telegram_user_id()

            unix_start_date = int(datetime.fromisoformat(start_date.replace("Z", "+00:00")).timestamp())
            number_len = len(str(unix_start_date))
            index = (unix_start_date % (number_len - 2)) + 1
            score_per_game = {"Candles": 500, "Tiles": random.randint(int(max_points * 0.1), max_points) if max_points > 200 else max_points}
            score = str(2 * (unix_start_date + score_per_game[mini_game_id]))

            cipher = ""
            for i in range(1, number_len + 1):
                if i == index:
                    cipher += "0"
                else:
                    cipher += str(randint(0, 9))

            sig = base64.b64encode(hashlib.sha256(f"{get_salt('salt_')}{score}{get_salt('_salt')}".encode()).digest()).decode()

            cipher_string = "|".join([cipher, user_id, mini_game_id, score, sig])
            minigame_cipher = base64.b64encode(cipher_string.encode()).decode()
            return minigame_cipher

        except:
            return minigame_cipher

    def _buy_upgrade(self, upgradeId: str) -> dict:
        try:
            upgrades_for_buy_response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            upgrades_for_buy_response.raise_for_status()

            upgradesForBuy = upgrades_for_buy_response.json().get('upgradesForBuy')
            for upgrade in upgradesForBuy:
                if upgradeId == upgrade['id']:
                    if upgrade.get('isAvailable') and not upgrade.get('isExpired'):
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        response.raise_for_status()

                        upgrade_name = upgrade.get('name')
                        upgrade_level = upgrade.get('level')
                        upgrade_available = upgrade.get('isAvailable')
                        upgrade_expire = upgrade.get('isExpired')

                        print(f"✅  Карта `{upgrade_name}` улучшена · ⭐️ {upgrade_level + 1} уровень")

                    elif upgrade_available and upgrade_expire:
                        logging.error(f"🚫  Карта `{upgrade_name}` недоступна для улучшения. Время на покупку истекло")

                    elif not upgrade_available:
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        buy_upgrade_response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        response.raise_for_status()

                        error_message = buy_upgrade_response.json().get('error_message')
                        logging.error(f"🚫  Не удалось улучшить карту `{upgrade_name}`. {error_message}")
                        return error_message

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                remain = remain_time(upgrade['cooldownSeconds'])
                print(f"🚫  Не удалось улучшить карту `{upgrade['name']}`. Карта будет доступна для улучшения через: {remain}")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _collect_upgrades_info(self) -> dict:
        try:
            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            cipher = self._get_daily_cipher()
            combo = self._get_daily_combo()

            total_price, total_profit, cards, cards_info = 0, 0, [], ''
            upgradesForBuy = response.json()['upgradesForBuy']
            for upgradeId in combo['combo']:
                for upgrade in upgradesForBuy:
                    if upgradeId == upgrade['id']:
                        available = upgrade['isAvailable']
                        if available:
                            available = f"✅  {GREEN}Карта доступна для улучшения{WHITE}"
                            total_price += upgrade['price']
                            total_profit += upgrade['profitPerHourDelta']
                        else:
                            error = self._buy_upgrade(upgrade['id'])
                            available = f"🚫  {RED}Карта недоступна для улучшения ({error}){WHITE}"

                        cards.append({'description': f"{available} \n"
                                                     f"🏷  {LIGHT_YELLOW}{upgrade['name']} • {upgrade['section']}{WHITE} \n"
                                                     f"💰  {YELLOW}{upgrade['price']:,}{WHITE} \n"
                                                     f"📈  {MAGENTA}+{upgrade['profitPerHourDelta']:,} в час{WHITE} \n"
                                                     f"⭐️  {DARK_GRAY}{upgrade['level']} уровень{WHITE} \n".replace(',', ' '),
                                      'id': upgrade['id'],
                                      'available': upgrade['isAvailable']})

                        if upgrade['isAvailable']:
                            available = f"{GREEN}{upgrade['isAvailable']}{WHITE}"
                        else:
                            available = f"{RED}{upgrade['isAvailable']}{WHITE}"
                        cards_info += f"{upgrade['name']} · {available} | "

            summary = f"📊  {LIGHT_YELLOW}Общая прыбыль:{WHITE}  {MAGENTA}+{total_profit:,} в час {WHITE}\n" \
                      f"🌟  {LIGHT_YELLOW}Общая стоимость:{WHITE} {YELLOW}{total_price:,}{WHITE}".replace(',', ' ')

            logging.warning(f"⚙️  {cards_info}{YELLOW}💰 {total_price:,}{WHITE} | {MAGENTA}📈 +{total_profit:,}{WHITE}")
            return {'cards': cards, 'summary': summary, 'cipher': cipher, 'combo_date': combo['date']}

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _sync(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()
            clicker_user = response.json().get('clickerUser')
            return clicker_user

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"🚫  HTTP ошибка: {http_err}")

    def daily_info(self) -> str:
        try:
            upgrades_info = self._collect_upgrades_info()
            balance = self._get_balance()
            cipher = upgrades_info.get('cipher')
            morse = text_to_morse(cipher)
            combo = '\n'.join(card['description'] for card in upgrades_info.get('cards'))

            result = {'date': f"📆  {datetime.today().date()} (текущая дата)\n📆  {upgrades_info.get('combo_date')} (дата комбо)",
                      'cipher': f"📇  {LIGHT_YELLOW}Шифр:{WHITE}  {cipher} | {morse} |",
                      'summary': f"{upgrades_info.get('summary')}",
                      'combo': combo}

            info = f"\n{result['date']} \n\n"
            info += f"{result['combo']} \n"
            info += f"{result['cipher']} \n\n"
            info += f"{result['summary']} \n\n"
            info += f"💰  {LIGHT_YELLOW}Баланс:{WHITE} {balance['balanceCoins']:,} \n"
            info += f"💰  {LIGHT_YELLOW}Всего: {WHITE} {balance['total']:,} \n"
            info += f"🔑  {LIGHT_YELLOW}Ключей:{WHITE} {balance['keys']:,}\n"
            if '🚫' in result['combo']:
                info += "\n⚠️  Сегодня вам не все карты доступны".replace(',', ' ')
            return info

        except Exception as e:
            logging.error(e)

    def complete_taps(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clickerUser = response.json().get('clickerUser')
            availableTaps = int(clickerUser.get('availableTaps'))
            maxTaps = int(clickerUser.get('maxTaps'))
            earnPerTap = int(clickerUser.get('earnPerTap'))
            tapsRecoverPerSec = int(clickerUser.get('tapsRecoverPerSec'))

            total_remain_time = maxTaps / tapsRecoverPerSec
            current_remain_time = availableTaps / tapsRecoverPerSec

            if availableTaps == maxTaps:
                count = int(maxTaps / earnPerTap)
                availableTaps = int(maxTaps - (count * earnPerTap))

                json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                taps_response = requests.post(f'{self.base_url}/clicker/tap', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                taps_response.raise_for_status()

                print(f"✅  Тапы выполнены")

            else:
                remain = remain_time(int(total_remain_time - current_remain_time))
                print(f"🚫  Тапы еще не накопились. Следующие тапы через: {remain}")

            boostsForBuy = requests.post(f'{self.base_url}/clicker/boosts-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN)).json().get('boostsForBuy')
            for boost in boostsForBuy:
                if boost['id'] == 'BoostFullAvailableTaps':
                    remain = boost['cooldownSeconds']
                    if remain == 0:
                        json_data = {'boostId': boost['id'], 'timestamp': int(time.time())}
                        boost_response = requests.post(f'{self.base_url}/clicker/buy-boost', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        boost_response.raise_for_status()

                        print(f"✅  Использован буст")

                        count = int(maxTaps / earnPerTap)
                        json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                        taps_response = requests.post(f'{self.base_url}/clicker/tap', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        taps_response.raise_for_status()

                        print(f"✅  Тапы выполнены")

                    else:
                        print(f"🚫  Буст еще не готов. Следующий буст через: {remain_time(remain)}. {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} доступно")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
                logging.error(traceback.format_exc())

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_tasks(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/list-tasks', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            task_list = response.json().get('tasks')
            any_completed = False
            for task in task_list:
                if not task.get('isCompleted'):
                    task_id = task.get('id')
                    json_data = {'taskId': task_id}
                    check_task = requests.post(f'{self.base_url}/clicker/check-task', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                    check_task.raise_for_status()

                    print(f"⭐️  Задание `{task_id}` выполнено")
                    any_completed = True

            if any_completed:
                print("✅  Все задания выполнены")

            else:
                print("ℹ️  Все задания сегодня уже выполнены")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_chipher(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            cipher = response.json().get('dailyCipher')
            remain = remain_time(cipher.get('remainSeconds'))
            next_cipher = f"Следующий шифр будет доступен через: {remain}"

            isClaimed = cipher.get('isClaimed')
            if not isClaimed:
                cipher = self._get_daily_cipher().upper()
                json_data = {'cipher': cipher}
                claim_cipher = requests.post(f'{self.base_url}/clicker/claim-daily-cipher', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                claim_cipher.raise_for_status()

                print(f"✅  Ежедневный шифр получен. {next_cipher}")

            else:
                print(f"ℹ️  Шифр сегодня уже получен. {next_cipher}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_combo(self, buy_anyway=False):
        try:
            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            combo = response.json().get('dailyCombo')
            remain = remain_time(combo.get('remainSeconds'))
            next_combo = f"Следующее комбо через: {remain}"

            isClaimed = combo.get('isClaimed')
            if not isClaimed:
                upgrades_info = self._collect_upgrades_info()
                cards = upgrades_info.get('cards')

                if all(card['available'] for card in cards):
                    for upgrade in cards:
                        self._buy_upgrade(upgrade['id'])
                    claim_combo = requests.post(f'{self.base_url}/clicker/claim-daily-combo', headers=self._get_headers(self.HAMSTER_TOKEN))
                    claim_combo.raise_for_status()

                    print(f"✅  Ежедневное комбо выполнено. {next_combo}")

                if buy_anyway:
                    for upgrade in cards:
                        self._buy_upgrade(upgrade['id'])
                    print(f"🚫  Ежедневное комбо не выполнено. Были куплены только доступные карты")
            else:
                print(f"ℹ️  Комбо сегодня уже получено. {next_combo}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_minigame(self, game_id):
        try:
            config_response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            config_response.raise_for_status()

            config_response_data = config_response.json()
            minigame = config_response_data.get('dailyKeysMiniGames').get(game_id)
            remain = remain_time(minigame.get('remainSeconds'))
            max_points = int(config_response_data.get('dailyKeysMiniGames').get('Tiles').get('maxPoints'))
            next_minigame = f"Следующая миниигра будет доступна через: {remain}"
            next_attempt = remain_time(minigame.get('remainSecondsToNextAttempt'))
            bonus_keys = minigame.get('bonusKeys')
            remain_points = minigame.get('remainPoints')

            isClaimed = minigame.get('isClaimed')
            if not isClaimed:
                if minigame.get('id') == 'Tiles':
                    bonus_for_one_point = self.bonus_for_one_point(minigame)
                    max_coins = bonus_for_one_point * max_points
                    claimed_points = max_points - remain_points
                    available_points = max_points - claimed_points
                    print(f"{YELLOW}За 1 балл вы получаете монет:  {LIGHT_BLUE}{bonus_for_one_point}{WHITE} | Портрачено: {claimed_points} | Осталось: {available_points}\n"
                          f"{YELLOW}Максимальное количество монет: {LIGHT_YELLOW}{max_coins:,}{WHITE}\n".replace(',', ' '))

                json_data = {'miniGameId': game_id}
                start_game = requests.post(f'{self.base_url}/clicker/start-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                start_game.raise_for_status()

                initial_balance = int(start_game.json().get('clickerUser').get('balanceCoins'))
                print(f"{YELLOW}Баланс: {LIGHT_MAGENTA}{initial_balance:,}{WHITE}".replace(',', ' '))

                current_balance = int(self._sync().get('balanceCoins'))
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                print(f"{YELLOW}Баланс: {balance} | пассивный".replace(',', ' '))

                cipher = self._get_mini_game_cipher(minigame)
                json_data = {'cipher': cipher, 'miniGameId': game_id}
                end_game = requests.post(f'{self.base_url}/clicker/claim-daily-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                end_game.raise_for_status()

                end_game_data = end_game.json()
                current_balance = int(self._sync().get('balanceCoins'))
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                bonus = f"{LIGHT_BLUE}+{int(end_game_data.get('bonus')):,}{WHITE}"
                print(f"{YELLOW}Баланс: {balance} [{bonus}] | пассивынй + бонус\n".replace(',', ' '))

                if bonus_keys == 0:
                    print(f"✅  Миниигра {game_id} пройдена. {next_minigame}")
                else:
                    print(f"✅  Миниигра {game_id} пройдена. Получено ключей: {bonus_keys}. {next_minigame}")

            else:
                print(f"ℹ️  Миниигра {game_id} сегодня уже пройдена. {next_minigame}")

        except requests.exceptions.HTTPError as http_err:
            if config_response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле\n🚫  {http_err}")

            elif config_response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле\n🚫  {http_err}")

            elif end_game.json().get('error_code') == 'DAILY_KEYS_MINI_GAME_WRONG':
                print(f"\n🚫  Не удалось пройти Миниигру {game_id}\n"
                      f"⚠️  Кажется разрабы хомяка снова поменяли шифр. Обновите код с помощью файла `UPDATE.bat`\n"
                      f"ℹ️  Если обновление не поможет, то подождите. Мы уже добываем для вас новый шифр  🫡\n")

            elif start_game.json().get('error_code') == 'KEYS-MINIGAME_WAITING':
                print(f"🚫  Миниигра не доступна. До следующей попытки осталось: {next_attempt}")

            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}\n")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

    def send_balance_to_group(self, bot_token, update_time_sec=7200, chat_id=None):
        try:
            while True:
                info = self._get_balance()
                user_id = self._get_telegram_user_id()

                update_date = datetime.datetime.fromtimestamp(info['date']).strftime('%Y-%m-%d %H:%M:%S')
                result = f"💰  Баланс: {info['balanceCoins']:,} \n" \
                         f"⭐️  Всего: {info['total']:,} \n" \
                         f"🆔  ID пользователя: {user_id} \n" \
                         f"🔄  Обновление: {update_date}"
                balance = result.replace(',', ' ')

                if chat_id is not None:
                    response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": chat_id, "text": balance})
                    response.raise_for_status()
                else:
                    response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": self.GROUP_ID, "text": balance})
                    response.raise_for_status()

                print(f"✅  {update_date} · Баланс успешно отправлен в группу")
                time.sleep(update_time_sec)

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def apply_promocode(self, promoCode, promo_id):
        try:
            response = requests.post(f'{self.base_url}/clicker/get-promos', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            keys_today = 0
            states = response.json().get('states')
            for state in states:
                try:
                    if state['promoId'] == promo_id:
                        keys_today = state['receiveKeysToday']
                        remain = remain_time(state['receiveKeysRefreshSec'])
                        next_keys = f"Следующие ключи будут доступны через: {remain}"
                except:
                    keys_today = 0

            promos = response.json()['promos']
            for promo in promos:
                if promo['promoId'] == promo_id:
                    keys_limit = promo['keysPerDay']
                    promo_title = promo['title']['en']

            if keys_today == keys_limit:
                print(f"ℹ️  Все ключи в игре `{promo_title}` сегодня уже получены. {next_keys}")
            else:
                print(f"{LIGHT_YELLOW}🔄  Активация промокода `{promoCode}`...{WHITE}")
                json_data = {'promoCode': promoCode}
                response = requests.post('https://api.hamsterkombatgame.io/clicker/apply-promo', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                response.raise_for_status()
                time.sleep(1)
                print(f"{LIGHT_GREEN}🎉  Промокод активирован. Получено ключей сегодня: {keys_today + 1}/{keys_limit}{WHITE}\n")
            time.sleep(1)

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Не удалось активировать промокод: {e}\n{traceback.format_exc()}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

    async def get_promocodes(self, count=1, apply_promo=False, prefix=None, spinner=None):
        """
        :param spinner:
        :param prefix:
        :param count:  Количество промокодов для генерации
        :param apply_promo: применять ли полученные промокоды в аккаунте хомяка (необязательно)
        """

        games_data = get_games_data()['apps']

        for promo in games_data:
            if promo['prefix'] == prefix:
                APP_TOKEN = promo['appToken']
                PROMO_ID = promo['promoId']
                EVENTS_DELAY = promo['registerEventTimeout']
                EVENTS_COUNT = promo['eventsCount']
                TITLE = promo['title']
                TEXT = promo['text']
                EMOJI = promo['emoji']

        async def delay_random():
            return random.random() / 3 + 1

        async def __generate_client_id() -> str:
            timestamp = int(time.time() * 1000)
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
            return f"{timestamp}-{random_numbers}"

        async def __get_client_token(session, client_id) -> Any | None:
            url = 'https://api.gamepromo.io/promo/login-client'
            headers = {'Content-Type': 'application/json'}
            payload = {'appToken': APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    response.raise_for_status()
                    return data.get('clientToken')

            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    logging.error(f"🚫  Не удалось начать генерацию. Превышено количетсво запросов")
                    return None

        async def __emulate_progress(session, client_token) -> Any | None:
            url = 'https://api.gamepromo.io/promo/register-event'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    response.raise_for_status()
                    return data.get('hasCode')

            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    logging.error(f"🚫  Не удалось начать генерацию. Превышено количетсво запросов")
                    return None

        async def __get_promocode(session, client_token) -> Any | None:
            url = 'https://api.gamepromo.io/promo/create-code'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    response.raise_for_status()
                    if data['promoCode'] == "" or data['promoCode'] == " ":
                        return None
                    else:
                        return data['promoCode']

            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    logging.error(f"🚫  Не удалось начать генерацию. Превышено количетсво запросов")
                return None

        async def __key_generation(session, index, keys_count) -> str | None:
            client_id = await __generate_client_id()
            client_token = await __get_client_token(session, client_id)
            time.sleep(1)

            for n in range(EVENTS_COUNT):
                await asyncio.sleep(EVENTS_DELAY * await delay_random() / 1000)
                try:
                    has_code = await __emulate_progress(session, client_token)
                except Exception as error:
                    logging.warning(f'[{index}/{keys_count}] {RED}Progress emulation failed: {error}{WHITE}')
                    return None

                print(f"{LIGHT_BLUE}{prefix}{WHITE} [{index}/{keys_count}] · Статус: {(n + 1) / EVENTS_COUNT * 100:.0f}%")
                if has_code:
                    break

            try:
                promoCode = await __get_promocode(session, client_token)
                print(f'{LIGHT_BLUE}{prefix}{WHITE} [{index}/{keys_count}] · Статус: {generation_status(promoCode)}')
                if promoCode:
                    return promoCode
                else:
                    return 'None'

            except Exception as error:
                logging.error(error)

        async def __start_generate(keys_count):
            remain = remain_time((EVENTS_COUNT * EVENTS_DELAY) / 1000)
            print(f"\n{LIGHT_YELLOW}`{TITLE}` · Генерируется промокодов: {keys_count}{WHITE} ~ {remain}")
            print(f'{YELLOW}{TEXT}{WHITE}')

            loading_event = asyncio.Event()
            spinner_task = asyncio.create_task(loading_v2(loading_event, spinner))

            async with aiohttp.ClientSession() as session:
                tasks = [__key_generation(session, i + 1, keys_count) for i in range(keys_count)]
                keys = await asyncio.gather(*tasks)
                loading_event.set()
                await spinner_task
            return [key for key in keys if key]

        promocodes = await __start_generate(count)

        line_before()
        result = f"\n*{EMOJI} {TITLE}*\n*Промокоды: *\n"
        for promocode in promocodes:
            result += f"·  `{promocode}`\n"
        print(result.replace('*', '').replace('`', ''))

        if apply_promo:
            settings = load_settings()
            settings['send_to_group'] = False
            settings['save_to_file'] = False
            save_settings(settings)

            print(f'⚠️  {LIGHT_YELLOW}Промокоды не будут отправленны в группу и не записаны в файл{WHITE}\n')
            for promocode in promocodes:
                self.apply_promocode(promocode, PROMO_ID)

        if load_setting('send_to_group'):
            try:
                telegram_response = requests.post(f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage", data={"chat_id": self.GROUP_ID, "parse_mode": "Markdown", "text": result})
                telegram_response.raise_for_status()
                time.sleep(3)
                print(f"Промокоды `{TITLE}` были отправлены в группу: `{self.GROUP_URL}`")

            except requests.exceptions.HTTPError:
                logging.error(f"🚫  Ошибкка во время запроса к телеграм API\n{telegram_response.status_code}")
            except Exception as e:
                logging.error(f"🚫  Произошла ошибка: {e}")

        if load_setting('save_to_file'):
            if not os.path.exists('generated keys'):
                os.makedirs('generated keys')

            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated keys', f'generated_keys ({TITLE}).txt')
            with open(file_path, 'w') as file:
                file.write(result.replace('*', '').replace('`', ''))
                print(f"Промокоды `{TITLE}` сохранены в файл:\n`{file_path}`")

    def evaluate_cards(self) -> list:
        response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
        response.raise_for_status()

        evaluated_cards = []
        upgrades = response.json()['upgradesForBuy']
        for card in upgrades:
            if card['isAvailable'] and not card['isExpired']:
                if card["profitPerHourDelta"] != 0:
                    payback_seconds = int(card["price"] / card["profitPerHour"]) * 3600
                    card["payback_period"] = remain_time(payback_seconds)
                    card["payback_days"] = f"{payback_seconds / 86400:.0f}"
                    card["profitability_ratio"] = (card["profitPerHour"] / card["price"]) * 100
                else:
                    card["payback_period"] = float('inf')
                    card["profitability_ratio"] = 0

                evaluated_cards.append(card)
        sorted_cards = sorted(evaluated_cards, key=lambda x: x["profitability_ratio"], reverse=True)
        return sorted_cards[:20]

    def get_account_info(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/auth/account-info', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            account_info = response.json()['accountInfo']['telegramUsers'][0]
            return account_info

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

    def login(self):
        settings = load_settings()
        lang = load_setting('lang').lower()
        try:
            response = requests.post('https://api.hamsterkombatgame.io/auth/account-info', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            account_info = response.json()['accountInfo']['telegramUsers'][0]
            username = account_info.get('username', 'n/a')
            first_name = account_info.get('firstName', 'n/a')
            last_name = account_info.get('lastName', 'n/a')

            print(localized_text('sign_in', lang, LIGHT_GRAY, first_name, last_name, username, WHITE))

            settings['hamster_token'] = True
            save_settings(settings)

        except requests.exceptions.HTTPError as http_err:
            print(f"⚠️  {RED}HAMSTER_TOKEN не указан в вашем .env файле, либо вы указали его неверно.{WHITE}\n"
                  f"⚠️  {YELLOW}Все функции связанные с аккаунтом Hamster Kombat недоступны!{WHITE}\n")
            settings['hamster_token'] = False
            save_settings(settings)

            logging.warning(http_err)
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

    def get_cooldowns(self) -> dict:
        result = {}
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clickerUser = response.json().get('clickerUser')
            availableTaps = int(clickerUser.get('availableTaps'))
            maxTaps = int(clickerUser.get('maxTaps'))
            tapsRecoverPerSec = clickerUser.get('tapsRecoverPerSec')
            total_remain_time = (maxTaps / tapsRecoverPerSec) / 60
            current_remain_time = (availableTaps / tapsRecoverPerSec) / 60
            remain_taps = total_remain_time - current_remain_time
            if remain_taps == 0:
                result['taps'] = True
            else:
                result['taps'] = False
                result['taps_remain'] = f"{remain_taps:.0f}"

            response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            result['cipher'] = response.json()['dailyCipher']['isClaimed']
            result['key'] = response.json().get('dailyKeysMiniGame').get('isClaimed')
            result['combo'] = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN)).json()['dailyCombo']['isClaimed']

            response = requests.post('https://api.hamsterkombatgame.io/clicker/list-tasks', headers=self._get_headers(self.HAMSTER_TOKEN))
            task_list = response.json().get('tasks', [])
            if all(task['isCompleted'] for task in task_list):
                result['tasks'] = True
            else:
                result['tasks'] = False
            return result

        except:
            return result

    def bonus_for_one_point(self, mini_game):
        json_data = {'miniGameId': mini_game.get('id')}
        requests.post(f'{self.base_url}/clicker/start-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)

        cipher = self._get_mini_game_cipher(mini_game, one_point=True)
        json_data = {'cipher': cipher, 'miniGameId': mini_game.get('id')}
        end_game = requests.post(f'{self.base_url}/clicker/claim-daily-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
        bonus = int(end_game.json().get('bonus'))
        return bonus

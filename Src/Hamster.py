import base64
import datetime
import json
import logging
import os
import random
import threading
import time
import traceback
import uuid
from random import randint

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as BS
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

from Src.utils import WHITE, YELLOW, LIGHT_YELLOW, LIGHT_GREEN, GREEN, RED, CYAN, MAGENTA, LIGHT_MAGENTA, LIGHT_CYAN, LIGHT_BLUE, DARK_GRAY, \
    text_to_morse, remain_time, line_after

load_dotenv()


class HamsterKombatClicker:

    def __init__(self, hamster_token, show_warning=False):
        """
        :param hamster_token: Ваш токен хомяка из браузерной версии игры
        """

        self.HAMSTER_TOKEN = hamster_token
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        self.GROUP_ID = os.getenv('GROUP_ID')
        self.GROUP_URL = os.getenv('GROUP_URL')

        self.base_url = 'https://api.hamsterkombatgame.io'

        if self.HAMSTER_TOKEN == 'XXX':
            logging.error(f'Отсутствует значение HAMSTER_TOKEN в вашем .env')
            exit(1)

        if show_warning:
            settings = ['BOT_TOKEN', 'GROUP_ID', 'GROUP_URL']
            missing_values = [value for value in settings if os.getenv(value) == 'XXX']
            if len(missing_values) > 0:
                logging.warning(f'{YELLOW}Следующие значения среды отсутствуют в вашем .env файле: {", ".join(missing_values)}{WHITE}')

    def _get_headers(self, hamster_token):
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

    def _get_telegram_user_id(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            return response.json()['clickerUser']['id']

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

            date = f"{date_block[0].text.split(':')[-1].strip()} {datetime.datetime.today().year}"
            combo_from_site = [item.text.strip() for item in combo_block]
            combo_ids = []

            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            upgradesForBuy = response.json()['upgradesForBuy']
            for upgrade in upgradesForBuy:
                for upgrade_name in combo_from_site:
                    name_from_site = str(upgrade_name.strip().lower())
                    name_from_hamster = str(upgrade['name'].strip().lower())

                    match = fuzz.partial_ratio(name_from_site, name_from_hamster)
                    if match > 90:
                        combo_ids.append(upgrade['id'])

            print(f"⚙️  Combo: {combo_ids} · Date: {date}")
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
            print(f"⚙️  Cipher:  {cipher}")
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

    def _get_balance(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clicker = response.json()['clickerUser']
            return {
                'balanceCoins': int(clicker['balanceCoins']),
                'total': int(clicker['totalCoins']),
                'keys': int(clicker['balanceKeys']),
                'date': int(clicker['lastSyncUpdate'])
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

    def _activity_cooldowns(self):
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
            daily_minigame = config_data.get('dailyKeysMiniGame', {})
            remain_minigame = remain_time(daily_minigame.get('remainSeconds', 0))
            result.append({'minigame': {'remain': remain_minigame, 'isClaimed': daily_minigame.get('isClaimed', False)}})

            response = requests.post('https://api.hamsterkombatgame.io/clicker/get-promos', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()
            promos = response.json().get('promos', [{}])
            states = response.json().get('states', [{}])
            promo_results = []
            for promo in promos:
                for state in states:
                    if promo['promoId'] == state['promoId']:
                        promo_name = promo['title']['en']
                        keys_today = state['receiveKeysToday']
                        remain_promo = remain_time(state['receiveKeysRefreshSec'])
                        is_claimed = True if keys_today == 4 else False
                        promo_results.append({'remain': remain_promo, 'keys': keys_today, 'name': promo_name, 'isClaimed': is_claimed})
            result.append({'promo': promo_results})

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
            logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _buy_upgrade(self, upgradeId: str) -> dict:
        try:
            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            upgradesForBuy = response.json()['upgradesForBuy']
            for upgrade in upgradesForBuy:
                if upgradeId == upgrade['id']:
                    if upgrade['isAvailable'] and not upgrade['isExpired']:
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        response.raise_for_status()
                        print(f"✅  Карта `{upgrade['name']}` улучшена · ⭐️ {upgrade['level'] + 1} уровень")

                    elif upgrade['isAvailable'] and upgrade['isExpired']:
                        logging.error(f"🚫  Карта `{upgrade['name']}` недоступна для улучшения. Время на покупку истекло")

                    elif not upgrade['isAvailable']:
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        logging.error(f"🚫  Не удалось улучшить карту `{upgrade['name']}`. {response.json()['error_message']}")
                        return response.json()['error_message']

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
            cipher = self._get_daily_cipher()
            combo = self._get_daily_combo()

            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

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
                                                     f"🏷  {CYAN}{upgrade['name']} • {upgrade['section']}{WHITE} \n"
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

            print(f"⚙️  {cards_info}{YELLOW}💰 {total_price:,}{WHITE} | {MAGENTA}📈 +{total_profit:,}{WHITE}")
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

    def daily_info(self):
        try:
            upgrades_info = self._collect_upgrades_info()
            balance = self._get_balance()
            cipher = upgrades_info['cipher']
            morse = text_to_morse(cipher)
            combo = '\n'.join(card['description'] for card in upgrades_info['cards'])

            result = {'date': f"📆  {datetime.datetime.today().date()} (текущая дата)\n📆  {upgrades_info['combo_date']} (дата комбо)",
                      'cipher': f"📇  {LIGHT_YELLOW}Шифр:{WHITE}  {cipher} | {morse} |",
                      'summary': f"{upgrades_info['summary']}",
                      'combo': combo}

            info = f"{result['date']} \n\n"
            info += f"{result['combo']} \n"
            info += f"{result['cipher']} \n\n"
            info += f"{result['summary']} \n\n"
            info += f"💰  {LIGHT_YELLOW}Баланс:{WHITE} {balance['balanceCoins']:,} \n"
            info += f"💰  {LIGHT_YELLOW}Всего:{WHITE} {balance['total']:,} \n"
            info += f"🔑  {LIGHT_YELLOW}Ключей:{WHITE} {balance['keys']:,} \n"
            if '🚫' in result['combo']:
                info += "\n⚠️  Сегодня вам не все карты доступны"
            time.sleep(1)
            line_after()
            return info.replace(',', ' ')

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

            task_list = response.json()['tasks']
            any_completed = False
            for task in task_list:
                if not task['isCompleted']:
                    json_data = {'taskId': task['id']}
                    check_task = requests.post(f'{self.base_url}/clicker/check-task', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                    check_task.raise_for_status()
                    print(f"⭐️  Задание `{task['id']}` выполнено")
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

            cipher = response.json()['dailyCipher']
            remain = remain_time(cipher['remainSeconds'])
            next_cipher = f"Следующий шифр будет доступен через: {remain}"

            isClaimed = cipher['isClaimed']
            if not isClaimed:
                cipher = self._get_daily_cipher().upper()
                json_data = {'cipher': cipher}
                claim_cipher = requests.post(f'{self.base_url}/clicker/claim-daily-cipher', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                claim_cipher.raise_for_status()
                print(f"⚡️  Ежедневный шифр получен. {next_cipher}")
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

            combo = response.json()['dailyCombo']
            remain = remain_time(combo['remainSeconds'])
            next_combo = f"Следующее комбо через: {remain}"

            isClaimed = combo['isClaimed']
            if not isClaimed:
                upgrades_info = self._collect_upgrades_info()
                cards = upgrades_info['cards']

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

    def complete_daily_minigame(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            minigame = response.json()['dailyKeysMiniGame']
            remain = remain_time(minigame['remainSeconds'])
            next_minigame = f"Следующая миниигра будет доступна через: {remain}"

            isClaimed = minigame['isClaimed']
            if not isClaimed:
                start_game = requests.post(f'{self.base_url}/clicker/start-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN))
                start_game.raise_for_status()
                print(f"{minigame['levelConfig']}")

                user_id = self._get_telegram_user_id()
                unix_time_from_start_game = f"0{randint(12, 26)}{random.randint(10000000000, 99999999999)}"[:10]
                cipher = base64.b64encode(f"{unix_time_from_start_game}|{user_id}".encode("utf-8")).decode("utf-8")
                json_data = {'cipher': cipher}
                end_game = requests.post(f'{self.base_url}/clicker/claim-daily-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                end_game.raise_for_status()
                print(f"✅  Миниигра пройдена. Получено ключей: {minigame['bonusKeys']}. {next_minigame}")
            else:
                print(f"ℹ️  Миниигра сегодня уже пройдена. {next_minigame}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def send_balance_to_group(self, bot_token, update_time_sec=7200):
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

            states = response.json()['states']
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
                print(f"⚠️  Активация промокода `{promoCode}`...")
                json_data = {'promoCode': promoCode}
                response = requests.post('https://api.hamsterkombatgame.io/clicker/apply-promo', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                response.raise_for_status()
                time.sleep(2)
                print(f"🎉  Промокод активирован. Получено ключей сегодня: {keys_today + 1}/{keys_limit}\n")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  HAMSTER_TOKEN не указан в вашем .env файле")
            elif response.status_code == 401:
                logging.error(f"🚫  Неверно указан HAMSTER_TOKEN в вашем .env файле")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

    def get_promocodes(self, count=1, send_to_group=False, apply_promo=False, prefix=None, save_to_file=True):
        """
        :param save_to_file:
        :param prefix:
        :param count:  Количество ключей для генерации
        :param send_to_group: отправлять ли результат в вашу группу (необязательно)
        :param apply_promo: применять ли полученные промокоды в аккаунте хомяка (необязательно)
        """

        with open('Src/playground_games_data.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())

        for promo in data['apps']:
            if promo['prefix'] == prefix:
                APP_TOKEN = promo['appToken']
                PROMO_ID = promo['promoId']
                EVENTS_DELAY = promo['registerEventTimeout']
                EVENTS_COUNT = promo['eventsCount']
                TITLE = promo['title']
                TEXT = promo['text']

                if prefix == "BIKE":
                    color_prefix = f"{LIGHT_YELLOW}{prefix}{WHITE}"
                elif prefix == "CUBE":
                    color_prefix = f"{LIGHT_BLUE}{prefix}{WHITE}"
                elif prefix == "CLONE":
                    color_prefix = f"{LIGHT_MAGENTA}{prefix}{WHITE}"
                elif prefix == "TRAIN":
                    color_prefix = f"{LIGHT_CYAN}{prefix}{WHITE}"

        def __generate_client_id() -> str:
            timestamp = int(time.time() * 1000)
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
            return f"{timestamp}-{random_numbers}"

        def __get_client_token(client_id) -> str:
            headers = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io'}
            json_data = {'appToken': APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

            try:
                response = requests.post(f'https://api.gamepromo.io/promo/login-client', headers=headers, json=json_data)
                response.raise_for_status()
                return response.json()['clientToken']
            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    logging.error(f"🚫  Не удалось начать генерацию. Превышено количетсво запросов")
                    return None

        def __emulate_progress(token) -> str:
            headers = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
            json_data = {'promoId': PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

            try:
                response = requests.post(f'https://api.gamepromo.io/promo/register-event', headers=headers, json=json_data)
                response.raise_for_status()
                return response.json().get('hasCode', False)
            except requests.exceptions.HTTPError:
                if response.status_code == 429:
                    logging.error(f"🚫  Не удалось начать генерацию. Превышено количетсво запросов")
                    return None

        def __get_promocode(token) -> str:
            headers = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
            json_data = {'promoId': PROMO_ID}

            response = requests.post(f'https://api.gamepromo.io/promo/create-code', headers=headers, json=json_data)
            response.raise_for_status()
            return response.json().get('promoCode', '')

        def __key_generation(keys_list, index, lock, progress_logged) -> None:
            client_id = __generate_client_id()
            print(f'{LIGHT_GREEN}[{index + 1}/{len(keys_list)}] `{TITLE}` Getting clientId successful{WHITE}')

            client_token = __get_client_token(client_id)
            print(f'{LIGHT_GREEN}[{index + 1}/{len(keys_list)}] `{TITLE}` Login successful{WHITE}')

            has_code = False
            with lock:
                if not progress_logged[0]:
                    time.sleep(2)
                    print(f'{YELLOW}{TEXT}{WHITE}')
                    progress_logged[0] = True

            for n in range(EVENTS_COUNT):
                delay = EVENTS_DELAY * (random.random() / 3 + 1)
                time.sleep(delay / 1000.0)
                print(f"{color_prefix} [{index + 1}/{len(keys_list)}] · Статус: {(n + 1) / EVENTS_COUNT * 100:.0f}%{WHITE}")

                has_code = __emulate_progress(client_token)
                if has_code:
                    break

            promoCode = __get_promocode(client_token)
            print(f'Сгенерированный промокод: {LIGHT_GREEN}`{promoCode}`{WHITE}')
            keys_list[index] = promoCode

        def __start_generate(keys_count):
            print(f"{LIGHT_YELLOW}`{TITLE}`. Генерируется промокодов: {keys_count}{WHITE}\n")

            keys_count = int(keys_count)
            if keys_count > 0:
                if not os.path.exists('data'):
                    os.makedirs('data')

                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', f'generated_keys ({TITLE}).txt')
                keys = [None] * keys_count
                threads = []
                lock_ = threading.Lock()
                logged = [False]
                generated_promocodes_text = ''

                with open(file_path, 'w') as file:
                    for n in range(keys_count):
                        thread = threading.Thread(target=__key_generation, args=(keys, n, lock_, logged))
                        threads.append(thread)
                        thread.start()

                    for thread in threads:
                        thread.join()

                    for key in keys:
                        generated_promocodes_text += f"{key}\n"

                    if save_to_file:
                        file.write(generated_promocodes_text)
                        print(f"Все промокоды сохранены в файл\n`{file_path}`")
                return generated_promocodes_text

            else:
                logging.error('Количество должно быть больше 0')
                exit(1)

        promocodes = __start_generate(count)
        if apply_promo:
            send_to_group = False
            for promocode in promocodes.split():
                self.apply_promocode(promocode, PROMO_ID)
                time.sleep(1)

        if send_to_group:
            try:
                response_telegram = requests.post(f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage", data={"chat_id": self.GROUP_ID, "text": promocodes})
                response_telegram.raise_for_status()
                time.sleep(3)
                print(f"{prefix} Промокоды были отправлены в группу `{self.GROUP_URL}`")

            except requests.exceptions.HTTPError as http_err:
                logging.warning(f"🚫  Ошибкка во время запроса к телеграм API\n{http_err}\n{traceback.format_exc()}")
            except Exception as e:
                logging.error(f"🚫  Произошла ошибка: {e}")

    def evaluate_cards(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
        response.raise_for_status()

        evaluated_cards = []
        upgrades = response.json()['upgradesForBuy']
        for card in upgrades:
            if card['isAvailable'] and not card['isExpired']:
                if card["profitPerHourDelta"] != 0:
                    card["payback_period"] = remain_time(int(card["price"] / card["profitPerHourDelta"]) * 3600)
                    card["profitability_ratio"] = card["profitPerHourDelta"] / card["price"]
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

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

    def login(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/auth/account-info', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            account_info = response.json()['accountInfo']['telegramUsers'][0]
            username = account_info['username']
            first_name = account_info['firstName']
            last_name = account_info['lastName']
            print(f"Вы вошли как {first_name} {last_name} ({username})\n")

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

        except requests.exceptions.RequestException as e:
            print(f"❌ Произошла ошибка: {e}")

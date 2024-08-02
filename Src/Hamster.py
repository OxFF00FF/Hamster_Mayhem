import base64
import datetime
import logging
import random
import re
import time
from random import randint
import requests
from utils import remain_time
from Src.utils import WHITE, MAGENTA, RED, GREEN, YELLOW, RESET, text_to_morse


class HamsterKombatClicker:

    def __init__(self, hamster_token):
        self.HEADERS = self._get_headers(hamster_token)

    def _get_headers(self, hamster_token):
        return {
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://hamsterkombat.io',
            'Referer': 'https://hamsterkombat.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'accept': 'application/json',
            'authorization': hamster_token,
            'content-type': 'application/json',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def _get_telegram_user_id(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
        if response.status_code == 200:
            clicker = response.json().get('clickerUser')
            user_ID = clicker.get('id')
            return user_ID

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def _get_daily_combo(self) -> dict:
        response = requests.post('https://api21.datavibe.top/api/GetCombo')
        if response.status_code == 200:
            logging.info(f"⚙️  Combo: {response.json()['combo']} · Date: {response.json()['date']}")
            return response.json()
        else:
            logging.error(f"{response.status_code} | {response.json()}")
            exit(1)

    def _get_daily_cipher(self) -> str:
        response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
        if response.status_code == 200:
            encoded_cipher = response.json()['dailyCipher']['cipher']
            cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
            logging.info(f"⚙️  Cipher:  {cipher}")
            return cipher

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

        else:
            logging.error(f"{response.status_code} | {response.json()}")
            exit(1)

    def _get_balance(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
        if response.status_code == 200:
            clicker = response.json()['clickerUser']
            balanceCoins = int(clicker['balanceCoins'])
            totalCoins = int(clicker['totalCoins'])
            lastSyncUpdate = clicker.get('lastSyncUpdate')
            keys = clicker['balanceKeys']

            return {'balanceCoins': balanceCoins, 'total': totalCoins, 'keys': keys, 'date': lastSyncUpdate}

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def _buy_upgrade(self, upgradeId: str) -> dict:
        if upgradeId:
            json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
            response = requests.post('https://api.hamsterkombatgame.io/clicker/buy-upgrade', headers=self.HEADERS, json=json_data)
            if response.status_code == 200:
                return response.json()

            elif response.json()['on'] == 'headers':
                logging.error(f"🚫  Токен не был предоставлен")
                exit(1)

            else:
                logging.error(f"🚫  Неверный upgradeId")
                exit(1)

    def _collect_upgrades_info(self) -> dict:
        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
        if response.status_code == 200:
            combo = self._get_daily_combo()
            cipher = self._get_daily_cipher()

            response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self.HEADERS)
            upgradesForBuy = response.json().get('upgradesForBuy', [])

            total_price = 0
            total_profit = 0
            cards = []
            cards_info = ''
            for card in combo['combo']:
                for upgrade in upgradesForBuy:
                    if card == upgrade['id']:
                        available = upgrade['isAvailable']
                        if available:
                            available = f"✅  Карта доступна для улучшения"
                            total_price += upgrade['price']
                            total_profit += upgrade['profitPerHourDelta']
                        else:
                            error = self._buy_upgrade(upgrade['id'])['error_message']
                            available = f"🚫  Карта недоступна для улучшения ({error})"

                        cards.append({'description': f"{available} \n"
                                                     f"🏷  {upgrade['name']} • {upgrade['section']}\n"
                                                     f"💰  {upgrade['price']:,} \n"
                                                     f"📈  +{upgrade['profitPerHourDelta']:,} в час \n"
                                                     f"⭐️  {upgrade['level']} уровень \n".replace(',', ' '),
                                      'id': upgrade['id'],
                                      'available': upgrade['isAvailable']})
                        if upgrade['isAvailable']:
                            available = f"{GREEN}{upgrade['isAvailable']}{WHITE}"
                        else:
                            available = f"{RED}{upgrade['isAvailable']}{WHITE}"
                        cards_info += f"{upgrade['name']} · {available} | "

            summary = f"📊  Общая прыбыль:  +{total_profit:,} в час \n" \
                      f"🌟  Общая стоимость: {total_price:,}".replace(',', ' ')

            logging.info(f"⚙️  {cards_info}{YELLOW}💰 {total_price:,}{RESET} | {MAGENTA}📈 +{total_profit:,}{RESET}")
            return {'cards': cards, 'summary': summary, 'cipher': cipher}

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def _daily_info(self):
        upgrades_info = self._collect_upgrades_info()
        cipher = upgrades_info['cipher']
        morse = text_to_morse(cipher)
        combo = '\n'.join(card['description'] for card in upgrades_info['cards'])

        result = {'date': f"📆  {datetime.datetime.today().date()}",
                  'cipher': f"📇  Шифр:  {cipher} | {morse} |",
                  'summary': f"{upgrades_info['summary']}",
                  'combo': combo}

        info = f"{result['date']} \n\n"
        info += f"{result['combo']} \n"
        info += f"{result['cipher']} \n\n"
        info += f"{result['summary']}"
        if '🚫' in result['combo']:
            info += "⚠️Сегодня вам не все карты доступны"
        logging.info(f"\n{info}")

        return result

    def complete_taps(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
        if response.status_code == 200:
            clickerUser = response.json().get('clickerUser')
            availableTaps = int(clickerUser.get('availableTaps'))
            maxTaps = int(clickerUser.get('maxTaps'))
            earnPerTap = int(clickerUser.get('earnPerTap'))
            tapsRecoverPerSec = int(clickerUser.get('tapsRecoverPerSec'))

            total_remain_time = maxTaps / tapsRecoverPerSec
            current_remain_time = availableTaps / tapsRecoverPerSec

            if availableTaps == maxTaps:
                count = maxTaps / earnPerTap
                availableTaps = maxTaps - (count * earnPerTap)

                json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=self.HEADERS, json=json_data)
                logging.info(f"✅  Тапы выполнены")
            else:
                remain = remain_time(int(total_remain_time - current_remain_time))
                logging.error(f"🚫  Тапы еще не накопились. Следующие тапы через: {remain}")

            response = requests.post('https://api.hamsterkombatgame.io/clicker/boosts-for-buy', headers=self.HEADERS)
            boostsForBuy = response.json().get('boostsForBuy')
            for boost in boostsForBuy:
                if boost['id'] == 'BoostFullAvailableTaps':
                    remain = remain_time(boost['cooldownSeconds'])
                    if remain == 0:
                        json_data = {'boostId': boost['id'], 'timestamp': int(time.time())}
                        requests.post('https://api.hamsterkombatgame.io/clicker/buy-boost', headers=self.HEADERS, json=json_data)
                        logging.info(f"✅  Использован буст")

                        json_data = {'count': int(count), 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                        requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=self.HEADERS, json=json_data)
                        logging.info(f"✅  Тапы выполнены")
                    else:
                        logging.error(f"🚫  Буст еще не готов. Следующий буст через: {remain}. {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} доступно")

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def complete_daily_tasks(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/list-tasks', headers=self.HEADERS)
        if response.status_code == 200:
            task_list = response.json().get('tasks', [])
            any_completed = False
            for task in task_list:
                if not task['isCompleted']:
                    json_data = {'taskId': task['id']}
                    requests.post('https://api.hamsterkombatgame.io/clicker/check-task', headers=self.HEADERS, json=json_data)
                    logging.info(f"⭐️  Задание `{task['id']}` выполнено")
                    any_completed = True
            if any_completed:
                logging.info("✅  Все задания выполнены")
            else:
                logging.info("ℹ️  Все задания сегодня уже выполнены")

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def complete_daily_chipher(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
        if response.status_code == 200:
            remain = remain_time(response.json()['dailyCipher']['remainSeconds'])
            isClaimed = response.json()['dailyCipher']['isClaimed']
            if not isClaimed:
                cipher = self._get_daily_cipher()['cipher'].upper()
                json_data = {'cipher': cipher}
                requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-cipher', headers=self.HEADERS, json=json_data)
                logging.info(f"⚡️  Ежедневный шифр получен ({cipher})")
            else:
                logging.info(f"ℹ️  Шифр сегодня уже получен. Следующий шифр будет доступен через: {remain}")

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def complete_daily_combo(self, buy_anyway=False, buy=False):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self.HEADERS)
        if response.status_code == 200:
            isClaimed = response.json()['dailyCombo']['isClaimed']

            remain = remain_time(response.json()['dailyCombo']['remainSeconds'])
            if not isClaimed:
                upgrades_info = self._collect_upgrades_info()
                cards = upgrades_info['cards']

                if buy_anyway:
                    for card in cards:
                        if card['available']:
                            upgradeId = card['id']
                            self._buy_upgrade(upgradeId)
                            logging.info(f"✅  Куплена карта `{upgradeId}`")
                        logging.info(f"🚫  Ежедневное комбо не выполнено. Были куплены только доступные карты")

                if buy:
                    if all(card['available'] for card in cards):
                        for card in cards:
                            upgradeId = card['id']
                            self._buy_upgrade(upgradeId)
                            logging.info(f"✅  Куплена карта `{upgradeId}`")
                        requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-combo', headers=self.HEADERS)
                        logging.info(f"✅  Ежедневное комбо выполнено")
                else:
                    self._daily_info()
            else:
                logging.info(f"ℹ️  Комбо сегодня уже получено. Следующее комбо через: {remain}")

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def complete_daily_minigame(self):
        response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
        if response.status_code == 200:
            isClaimed = response.json()['dailyKeysMiniGame']['isClaimed']
            keys = response.json()['dailyKeysMiniGame']['bonusKeys']
            remain = remain_time(response.json()['dailyKeysMiniGame']['remainSeconds'])

            if not isClaimed:
                levelConfig = response.json().get('dailyKeysMiniGame').get('levelConfig')
                logging.info(f"| {datetime.datetime.today().date()} | {levelConfig} |")

                start_game = requests.post('https://api.hamsterkombatgame.io/clicker/start-keys-minigame', headers=self.HEADERS)
                if start_game.status_code == 200:
                    match = re.search(pattern=r'Bearer (.*?)(\d+$)', string=self.HEADERS['authorization'])
                    if match:
                        user_id = match.group(2)
                        unix_time_from_start_game = f"0{randint(12, 26)}{random.randint(10000000000, 99999999999)}"[:10]
                        cipher = base64.b64encode(f"{unix_time_from_start_game}|{user_id}".encode("utf-8")).decode("utf-8")

                    json_data = {'cipher': cipher}
                    end_game = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame', headers=self.HEADERS, json=json_data)
                    if end_game.status_code == 200:
                        logging.info(f"✅  Миниигра пройдена. Получено ключей: {keys}. Следующая миниигра будет доступна через: {remain}")
                    else:
                        logging.error(f"{end_game.status_code} | {end_game.json()}")
                else:
                    match = re.search(pattern=r'Please wait (.*?) before next attempt', string=response.json().get('error_message'))
                    remain = remain_time(int(match.group(1).split('.')[0]))
                    logging.error(f"🚫  Миниигра недоступна. Следующая попытка через: {remain}")
            else:
                logging.info(f"ℹ️  Миниигра сегодня уже пройдена. Следующая миниигра будет доступна через: {remain}")

        elif response.json()['on'] == 'headers':
            logging.error(f"🚫  Токен не был предоставлен")
            exit(1)

    def send_balance_to_group(self, bot_token, group_id, update_time_sec=7200):
        while True:
            info = self._get_balance()
            user_id = self._get_telegram_user_id()

            update_date = datetime.datetime.fromtimestamp(info['date']).strftime('%Y-%m-%d %H:%M:%S')
            result = f"💰  Баланс: {info['balanceCoins']:,} \n" \
                     f"⭐️  Всего: {info['total']:,} \n" \
                     f"🆔  ID пользователя: {user_id} \n" \
                     f"🔄  Обновление: {update_date}"
            balance = result.replace(',', ' ')

            logging.info(balance.replace('\n', '| '))
            response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": group_id, "text": balance})
            if response.status_code == 200:
                logging.info(f"✅  Баланс успешно отправлен в группу\n")
            else:
                logging.error(response.json())

            time.sleep(update_time_sec)

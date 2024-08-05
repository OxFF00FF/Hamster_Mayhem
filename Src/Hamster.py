import base64
import datetime
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
from Src.utils import WHITE, MAGENTA, RED, GREEN, YELLOW, RESET, text_to_morse, remain_time, CYAN

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))


class HamsterKombatClicker:
    """

    """
    def __init__(self, hamster_token):
        self.HEADERS = self._get_headers(hamster_token)
        self.APP_TOKEN = os.getenv('APP_TOKEN')
        self.PROMO_ID = os.getenv('PROMO_ID')
        self.GROUP_URL = os.getenv('GROUP_URL')
        self.EVENTS_DELAY = 20000

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
            response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
            response.raise_for_status()

            return response.json()['clickerUser']['id']

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _get_daily_combo(self) -> dict:
        try:
            response = requests.post('https://api21.datavibe.top/api/GetCombo')
            response.raise_for_status()

            logging.info(f"⚙️  Combo: {response.json()['combo']} · Date: {response.json()['date']}")
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            logging.error(http_err)

        except Exception as e:
            logging.error(e)

    def _get_daily_cipher(self) -> str:
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
            response.raise_for_status()

            encoded_cipher = response.json()['dailyCipher']['cipher']
            cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
            logging.info(f"⚙️  Cipher:  {cipher}")
            return cipher

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _get_balance(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
            response.raise_for_status()

            clicker = response.json()['clickerUser']
            return {'balanceCoins': int(clicker['balanceCoins']),
                    'total': int(clicker['totalCoins']),
                    'keys': int(clicker['balanceKeys']),
                    'date': int(clicker['lastSyncUpdate'])}

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _buy_upgrade(self, upgradeId: str) -> dict:
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self.HEADERS)
            response.raise_for_status()

            upgradesForBuy = response.json()['upgradesForBuy']
            for upgrade in upgradesForBuy:
                if upgradeId == upgrade['id']:
                    if upgrade['isAvailable'] and not upgrade['isExpired']:
                        json_data = {'upgradeId': upgradeId, 'timestamp': time.time()}
                        buy_upgrade = requests.post('https://api.hamsterkombatgame.io/clicker/buy-upgrade', headers=self.HEADERS, json=json_data)
                        buy_upgrade.raise_for_status()

                        logging.info(f"✅  Карта `{upgrade['name']}` улучшена · ⭐️ {upgrade['level'] + 1} уровень")
                        return buy_upgrade.json()['upgradesForBuy']

                    if upgrade['isAvailable'] and upgrade['isExpired']:
                        json_data = {'upgradeId': upgradeId, 'timestamp': time.time()}
                        buy_upgrade = requests.post('https://api.hamsterkombatgame.io/clicker/buy-upgrade', headers=self.HEADERS, json=json_data)
                        buy_upgrade.raise_for_status()

                        logging.error(f"🚫  Карта `{upgrade['name']}` недоступна для улучшения. Время на покупку истекло")
                        return buy_upgrade.json()['error_message']

                    if not upgrade['isAvailable']:
                        json_data = {'upgradeId': upgradeId, 'timestamp': time.time()}
                        buy_upgrade = requests.post('https://api.hamsterkombatgame.io/clicker/buy-upgrade', headers=self.HEADERS, json=json_data).json()
                        buy_upgrade.raise_for_status()

                        logging.error(f"🚫  Не удалось улучшить карту `{upgrade['name']}`. {buy_upgrade['error_message']}")
                        return buy_upgrade.json()['error_message']

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def _collect_upgrades_info(self) -> dict:
        try:
            cipher = self._get_daily_cipher()
            combo = self._get_daily_combo()

            response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self.HEADERS)
            response.raise_for_status()

            total_price, total_profit, cards, cards_info = 0, 0, [], ''
            upgradesForBuy = response.json()['upgradesForBuy']
            for upgradeId in combo['combo']:
                for upgrade in upgradesForBuy:
                    if upgradeId == upgrade['id']:
                        available = upgrade['isAvailable']
                        if available:
                            available = f"✅  Карта доступна для улучшения"
                            total_price += upgrade['price']
                            total_profit += upgrade['profitPerHourDelta']
                        else:
                            error = self._buy_upgrade(upgrade['id'])
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

            logging.info(f"⚙️  {cards_info}{YELLOW}💰 {total_price:,}{RESET} | {MAGENTA}📈 +{total_profit:,}{WHITE}")
            return {'cards': cards, 'summary': summary, 'cipher': cipher}

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def daily_info(self):
        try:
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

        except Exception as e:
            logging.error(e)

    def complete_taps(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=self.HEADERS)
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

                json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': time.time()}
                taps_response = requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=self.HEADERS, json=json_data)
                taps_response.raise_for_status()
                logging.info(f"✅  Тапы выполнены")
            else:
                remain = remain_time(int(total_remain_time - current_remain_time))
                logging.error(f"🚫  Тапы еще не накопились. Следующие тапы через: {remain}")

            boostsForBuy = requests.post('https://api.hamsterkombatgame.io/clicker/boosts-for-buy', headers=self.HEADERS).json().get('boostsForBuy')
            for boost in boostsForBuy:
                if boost['id'] == 'BoostFullAvailableTaps':
                    remain = boost['cooldownSeconds']
                    if remain == 0:
                        json_data = {'boostId': boost['id'], 'timestamp': time.time()}
                        boost_response = requests.post('https://api.hamsterkombatgame.io/clicker/buy-boost', headers=self.HEADERS, json=json_data)
                        boost_response.raise_for_status()
                        logging.info(f"✅  Использован буст")

                        count = int(maxTaps / earnPerTap)
                        json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': time.time()}
                        taps_response = requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=self.HEADERS, json=json_data)
                        taps_response.raise_for_status()
                        logging.info(f"✅  Тапы выполнены")
                    else:
                        logging.error(f"🚫  Буст еще не готов. Следующий буст через: {remain_time(remain)}. {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} доступно")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
                logging.error(traceback.format_exc())

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_tasks(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/list-tasks', headers=self.HEADERS)
            response.raise_for_status()

            task_list = response.json()['tasks']
            any_completed = False
            for task in task_list:
                if not task['isCompleted']:
                    json_data = {'taskId': task['id']}
                    check_task = requests.post('https://api.hamsterkombatgame.io/clicker/check-task', headers=self.HEADERS, json=json_data)
                    check_task.raise_for_status()
                    logging.info(f"⭐️  Задание `{task['id']}` выполнено")
                    any_completed = True
            if any_completed:
                logging.info("✅  Все задания выполнены")
            else:
                logging.info("ℹ️  Все задания сегодня уже выполнены")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_chipher(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
            response.raise_for_status()

            cipher = response.json()['dailyCipher']
            remain = remain_time(['remainSeconds'])
            next_cipher = f"Следующий шифр будет доступен через: {remain}"

            isClaimed = cipher['isClaimed']
            if not isClaimed:
                cipher = self._get_daily_cipher().upper()
                json_data = {'cipher': cipher}
                claim_cipher = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-cipher', headers=self.HEADERS, json=json_data)
                claim_cipher.raise_for_status()
                logging.info(f"⚡️  Ежедневный шифр получен. {next_cipher}")
            else:
                logging.info(f"ℹ️  Шифр сегодня уже получен. {next_cipher}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_combo(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=self.HEADERS)
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
                    claim_combo = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-combo', headers=self.HEADERS)
                    claim_combo.raise_for_status()
                    logging.info(f"✅  Ежедневное комбо выполнено. {next_combo}")
                else:
                    for upgrade in cards:
                        self._buy_upgrade(upgrade['id'])
                    logging.info(f"🚫  Ежедневное комбо не выполнено. Были куплены только доступные карты")
            else:
                logging.info(f"ℹ️  Комбо сегодня уже получено. {next_combo}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")

        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def complete_daily_minigame(self):
        try:
            response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=self.HEADERS)
            response.raise_for_status()

            minigame = response.json()['dailyKeysMiniGame']
            remain = remain_time(minigame['remainSeconds'])
            next_minigame = f"Следующая миниигра будет доступна через: {remain}"

            isClaimed = minigame['isClaimed']
            if not isClaimed:
                start_game = requests.post('https://api.hamsterkombatgame.io/clicker/start-keys-minigame', headers=self.HEADERS)
                start_game.raise_for_status()
                logging.info(f"{minigame['levelConfig']}")

                user_id = self._get_telegram_user_id()
                unix_time_from_start_game = f"0{randint(12, 26)}{random.randint(10000000000, 99999999999)}"[:10]
                cipher = base64.b64encode(f"{unix_time_from_start_game}|{user_id}".encode("utf-8")).decode("utf-8")
                json_data = {'cipher': cipher}
                end_game = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame', headers=self.HEADERS, json=json_data)
                end_game.raise_for_status()
                logging.info(f"✅  Миниигра пройдена. Получено ключей: {minigame['bonusKeys']}. {next_minigame}")
            else:
                logging.info(f"ℹ️  Миниигра сегодня уже пройдена. {next_minigame}")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def send_balance_to_group(self, bot_token, group_id, update_time_sec=7200):
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

                response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": group_id, "text": balance})
                response.raise_for_status()

                logging.info(f"✅  {update_date} · Баланс успешно отправлен в группу")
                time.sleep(update_time_sec)

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                logging.error(f"🚫  Токен не был предоставлен")
            elif response.status_code == 401:
                logging.error(f"🚫  Предоставлен неверный токен")
            else:
                logging.error(f"🚫  HTTP ошибка: {http_err}")
        except Exception as e:
            logging.error(f"🚫  Произошла ошибка: {e}")

    def get_promocodes(self, count=1, send_to_group=False, bot_token=None, group_id=None):
        def __generate_client_id() -> str:
            timestamp = int(time.time() * 1000)
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
            return f"{timestamp}-{random_numbers}"

        def __get_client_token(client_id) -> str:
            headers = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io'}
            json_data = {'appToken': self.APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

            response = requests.post('https://api.gamepromo.io/promo/login-client', headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()['clientToken']

        def __emulate_progress(token) -> str:
            headers = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
            json_data = {'promoId': self.PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

            response = requests.post('https://api.gamepromo.io/promo/register-event', headers=headers, json=json_data)
            response.raise_for_status()
            return response.json().get('hasCode', False)

        def __get_promocode(token) -> str:
            HEADERS = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
            json_data = {'promoId': self.PROMO_ID}

            response = requests.post('https://api.gamepromo.io/promo/create-code', headers=HEADERS, json=json_data)
            response.raise_for_status()
            return response.json().get('promoCode', '')

        def __key_generation(keys_list, index, lock, progress_logged) -> None:
            client_id = __generate_client_id()
            logging.info(f'{GREEN}[{index + 1}] Getting clientId successful{WHITE}')

            client_token = __get_client_token(client_id)
            logging.info(f'{GREEN}[{index + 1}] Login successful{WHITE}')

            has_code = False
            time.sleep(3)
            with lock:
                if not progress_logged[0]:
                    logging.info(f'{YELLOW}Emulate progress... {WHITE}')
                    progress_logged[0] = True

            progress = 20
            for _ in range(7):
                delay = self.EVENTS_DELAY * (random.random() / 3 + 1)
                time.sleep(delay / 1000.0)

                has_code = __emulate_progress(client_token)
                logging.info(f"{CYAN}[{index + 1}/{len(keys_list)}] key · Status: {progress}%]{WHITE}")
                progress += 20
                if has_code:
                    break

            promoCode = __get_promocode(client_token)
            logging.info(f'Generated key: {GREEN}`{promoCode}`{WHITE}')
            keys_list[index] = promoCode

        def _start_generate(keys_count):
            keys_count = int(keys_count)
            logging.info(f"Генерируем {keys_count} ключей\n")
            if keys_count > 0:
                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_keys.txt')
                keys = [None] * keys_count
                threads = []
                lock_ = threading.Lock()
                logged = [False]
                keys_text = ''

                with open(file_path, 'w') as _:
                    pass

                with open(file_path, 'a') as file:
                    for e in range(keys_count):
                        thread = threading.Thread(target=__key_generation, args=(keys, e, lock_, logged))
                        threads.append(thread)
                        thread.start()

                    for thread in threads:
                        thread.join()

                    for key in keys:
                        keys_text += f"{key}\n"
                        file.write(f'{key}\n')
                logging.info(f"Все ключи сохранены в файл `{file_path}`")
                return keys_text

            else:
                logging.error('Количество ключей должно быть больше 0')
                exit(1)

        text = _start_generate(count)
        if send_to_group:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": group_id, "text": text}).raise_for_status()
            logging.info(f"Ключи был отправлены в группу `{self.GROUP_URL}`")


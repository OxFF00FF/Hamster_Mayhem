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

import aiohttp
import requests
from bs4 import BeautifulSoup as BS
from dotenv import load_dotenv
from fake_useragent import UserAgent
from fuzzywuzzy import fuzz

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.utils import text_to_morse, remain_time, get_games_data, line_before, generation_status, get_salt, localized_text, align_daily_info, align_summary, line_after, update_spinner, loading_v2

import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
config = ConfigDB()


class HamsterKombatClicker:

    def __init__(self, hamster_token):
        self.HAMSTER_TOKEN = hamster_token
        self.BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.CHAT_ID = os.getenv('CHAT_ID')
        self.GROUP_URL = os.getenv('GROUP_URL')
        self.base_url = 'https://api.hamsterkombatgame.io'

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

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def _get_daily_cipher(self) -> str:
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            encoded_cipher = response.json()['dailyCipher']['cipher']
            cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
            logging.info(cipher)
            return cipher

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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
                if task.get('id') == 'streak_days_special':
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
            remain = remain_time(int(total_remain_time - current_remain_time))

            if availableTaps == maxTaps:
                result.append({'taps': {'remain': 'n/a', 'isClaimed': True}})
            else:
                result.append({'taps': {'remain': remain, 'isClaimed': False}})

            return result

        except:
            return result

    def _get_promos(self) -> list:
        result = []
        try:
            response = requests.post(f'{self.base_url}/clicker/get-promos', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            promos = response.json().get('promos', [{}])
            states = response.json().get('states', [{}])

            for promo in promos:
                keys_per_day = promo['keysPerDay']
                for state in states:
                    if promo['promoId'] == state['promoId']:
                        promo_name = promo['title']['en']
                        recieved_keys = state['receiveKeysToday']
                        remain_promo = remain_time(state['receiveKeysRefreshSec'])
                        is_claimed = True if recieved_keys == keys_per_day else False
                        result.append({'remain': remain_promo, 'keys': recieved_keys, 'name': promo_name, 'isClaimed': is_claimed, "per_day": keys_per_day})
            return result

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
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

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
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
            score_per_game = {"Candles": 500, "Tiles": max_points}
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

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return minigame_cipher

    def _buy_upgrade(self, upgradeId: str) -> dict:
        try:
            upgrades_for_buy_response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            upgrades_for_buy_response.raise_for_status()

            upgradesForBuy = upgrades_for_buy_response.json().get('upgradesForBuy')
            for upgrade in upgradesForBuy:
                upgrade_name = upgrade.get('name')
                upgrade_level = upgrade.get('level')
                upgrade_available = upgrade.get('isAvailable')
                upgrade_expire = upgrade.get('isExpired')
                upgrade_cooldown = upgrade.get('cooldownSeconds', 1)

                if upgradeId == upgrade['id']:
                    if upgrade.get('isAvailable') and not upgrade.get('isExpired') and upgrade_cooldown == 0:
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        response.raise_for_status()

                        print(f"✅  {localized_text('info_card_upgraded', upgrade_name, upgrade_level+1)}")

                    elif upgrade_available and upgrade_expire:
                        logging.error(f"🚫  {localized_text('error_upgrade_not_avaialble_time_expired', upgrade_name)}")

                    else:
                        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
                        buy_upgrade_response = requests.post(f'{self.base_url}/clicker/buy-upgrade', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        print(buy_upgrade_response.json())
                        error_message = buy_upgrade_response.json().get('error_message')
                        print(f"🚫  {localized_text('error_upgrade_not_avaialble')} `{upgrade_name}`\n    {error_message}")
                        return error_message

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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
                            available = f"✅  {GREEN}{localized_text('available_to_buy')}{WHITE}"
                            total_price += upgrade['price']
                            total_profit += upgrade['profitPerHourDelta']
                        else:
                            error = self._buy_upgrade(upgrade['id'])
                            available = f"🚫  {RED}{localized_text('not_available_to_buy')} ({error}){WHITE}"

                        cards.append({'description': f"{available} \n"
                                                     f"🏷  {LIGHT_YELLOW}{upgrade['name']} • {upgrade['section']}{WHITE} \n"
                                                     f"💰  {YELLOW}{upgrade['price']:,}{WHITE} \n"
                                                     f"📈  {MAGENTA}+{upgrade['profitPerHourDelta']:,} {localized_text('per_hour')}{WHITE} \n"
                                                     f"⭐️  {DARK_GRAY}{upgrade['level']} {localized_text('level')}{WHITE} \n".replace(',', ' '),
                                      'id': upgrade['id'],
                                      'available': upgrade['isAvailable']})

                        if upgrade['isAvailable']:
                            available = f"{GREEN}{upgrade['isAvailable']}{WHITE}"
                        else:
                            available = f"{RED}{upgrade['isAvailable']}{WHITE}"
                        cards_info += f"{upgrade['name']} · {available} | "

            summary = f"📊  {LIGHT_YELLOW}{align_summary(localized_text('total_profit'))}{WHITE}{MAGENTA}+{total_profit:,} {localized_text('per_hour')} {WHITE}\n" \
                      f"🌟  {LIGHT_YELLOW}{align_summary(localized_text('total_price'))}{WHITE}{YELLOW}{total_price:,}{WHITE}".replace(',', ' ')

            logging.warning(f"⚙️  {cards_info}{YELLOW}💰 {total_price:,}{WHITE} | {MAGENTA}📈 +{total_profit:,}{WHITE}")
            return {'cards': cards, 'summary': summary, 'cipher': cipher, 'combo_date': combo['date']}

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def _sync(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()
            clicker_user = response.json().get('clickerUser')
            return clicker_user

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def daily_info(self) -> str:
        try:
            upgrades_info = self._collect_upgrades_info()
            balance = self._get_balance()
            purhase_counts = self.get_purhase_count()
            cipher = upgrades_info.get('cipher')
            morse = text_to_morse(cipher)
            combo = '\n'.join(card['description'] for card in upgrades_info.get('cards'))

            result = {
                'date': f"📆  {datetime.today().date()} ({localized_text('current_date')})\n"
                        f"📆  {upgrades_info.get('combo_date')} ({localized_text('combo_date')})",
                'cipher': f"📇  {LIGHT_YELLOW}{localized_text('cipher')}:{WHITE}  {cipher} | {morse} |",
                'summary': f"{upgrades_info.get('summary')}",
                'combo': combo}

            info = f"{result['date']} \n\n"
            info += f"{result['combo']} \n"
            info += f"{result['cipher']} \n\n"
            info += f"{result['summary']} \n\n"
            info += f"💰  {LIGHT_YELLOW}{align_daily_info(localized_text('balance'))}{WHITE}{balance['balanceCoins']:,}\n"
            info += f"💰  {LIGHT_YELLOW}{align_daily_info(localized_text('total'))}{WHITE}{balance['total']:,}\n"
            info += f"🔑  {LIGHT_YELLOW}{align_daily_info(localized_text('keys'))}{WHITE}{balance['keys']:,}\n"
            info += f"🔥  {LIGHT_YELLOW}{align_daily_info(localized_text('total_purhased_cards_count'))}{WHITE}{purhase_counts['cards_count']}\n"
            info += f"🔥  {LIGHT_YELLOW}{align_daily_info(localized_text('total_purhased_upgraqdes_count'))}{WHITE}{purhase_counts['upgrades_count']}"
            if '🚫' in result['combo']:
                info += f"\n\n⚠️  {localized_text('no_combo_today')}".replace(',', ' ')
            return info.replace(',', ' ')

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def complete_taps(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            clickerUser = response.json().get('clickerUser')
            availableTaps = int(clickerUser.get('availableTaps'))
            maxTaps = int(clickerUser.get('maxTaps'))
            earnPerTap = int(clickerUser.get('earnPerTap'))

            if availableTaps == maxTaps:
                count = int(maxTaps / earnPerTap)
                availableTaps = int(maxTaps - (count * earnPerTap))

                json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                taps_response = requests.post(f'{self.base_url}/clicker/tap', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                taps_response.raise_for_status()

                print(f"✅  {localized_text('info_taps_completed')}")

            else:
                print(f"🚫  {localized_text('info_no_accumulate_yet')}")

            boostsForBuy = requests.post(f'{self.base_url}/clicker/boosts-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN)).json().get('boostsForBuy')
            for boost in boostsForBuy:
                if boost['id'] == 'BoostFullAvailableTaps':
                    remain = boost['cooldownSeconds']
                    if remain == 0:
                        json_data = {'boostId': boost['id'], 'timestamp': int(time.time())}
                        boost_response = requests.post(f'{self.base_url}/clicker/buy-boost', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        boost_response.raise_for_status()

                        print(f"✅  {localized_text('info_boost_used')}")

                        count = int(maxTaps / earnPerTap)
                        json_data = {'count': count, 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                        taps_response = requests.post(f'{self.base_url}/clicker/tap', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                        taps_response.raise_for_status()

                        print(f"✅  {localized_text('info_taps_completed')}")

                    else:
                        remain = f"{LIGHT_MAGENTA}{remain_time(remain)}{WHITE}"
                        print(f"🚫  {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} {localized_text('boosts_available')}. {localized_text('info_next_boost_after')}: {remain}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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

                    print(f"⭐️  {localized_text('info_task_completed', task_id)}")
                    any_completed = True

            if any_completed:
                print(f"✅  {localized_text('info_all_tasks_complete')}")

            else:
                print(f"ℹ️  {localized_text('info_all_tasks_already_complete')}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def complete_daily_chipher(self):
        try:
            response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            cipher = response.json().get('dailyCipher')
            isClaimed = cipher.get('isClaimed')
            if not isClaimed:
                cipher = self._get_daily_cipher().upper()
                json_data = {'cipher': cipher}
                claim_cipher = requests.post(f'{self.base_url}/clicker/claim-daily-cipher', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                claim_cipher.raise_for_status()

                print(f"✅  {localized_text('info_cipher_completed')}")

            else:
                print(f"ℹ️  {localized_text('info_cipher_already_complete')}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def complete_daily_combo(self, buy_anyway=False):
        try:
            response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            combo = response.json().get('dailyCombo')
            isClaimed = combo.get('isClaimed')
            if not isClaimed:
                upgrades_info = self._collect_upgrades_info()
                cards = upgrades_info.get('cards')

                if all(card['available'] for card in cards):
                    for upgrade in cards:
                        self._buy_upgrade(upgrade['id'])
                    claim_combo = requests.post(f'{self.base_url}/clicker/claim-daily-combo', headers=self._get_headers(self.HAMSTER_TOKEN))
                    claim_combo.raise_for_status()

                    print(f"✅  {localized_text('info_combo_completed')}")

                if buy_anyway:
                    for upgrade in cards:
                        self._buy_upgrade(upgrade['id'])
                    print(f"🚫  {localized_text('warning_combo_not_complete')}")
            else:
                print(f"ℹ️  {localized_text('info_combo_already_complete')}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def complete_daily_minigame(self, game_id):
        try:
            config_response = requests.post(f'{self.base_url}/clicker/config', headers=self._get_headers(self.HAMSTER_TOKEN))
            config_response.raise_for_status()

            config_response_data = config_response.json()
            minigame = config_response_data.get('dailyKeysMiniGames').get(game_id)
            remain = f"{LIGHT_MAGENTA}{remain_time(minigame.get('remainSeconds'))}{WHITE}"
            max_points = int(config_response_data.get('dailyKeysMiniGames').get('Tiles').get('maxPoints'))
            next_minigame = f"{localized_text('info_next_minigame_after')}: {remain}"
            next_attempt = remain_time(minigame.get('remainSecondsToNextAttempt'))
            bonus_keys = minigame.get('bonusKeys')

            isClaimed = minigame.get('isClaimed')
            if not isClaimed:
                if minigame.get('id') == 'Tiles':
                    try:
                        one_point_bonus = self.bonus_for_one_point(minigame)
                        config.bonus_for_one_point = one_point_bonus
                    except:
                        one_point_bonus = config.bonus_for_one_point

                    max_coins = one_point_bonus * max_points
                    print(f"ℹ️  {YELLOW}{localized_text('info_coinf_for_one_point')}:  {LIGHT_BLUE}{one_point_bonus}{WHITE} \n"
                          f"{YELLOW}{localized_text('info_max_coins')}: {LIGHT_YELLOW}{max_coins:,}{WHITE}\n".replace(',', ' '))

                json_data = {'miniGameId': game_id}
                start_game = requests.post(f'{self.base_url}/clicker/start-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                start_game.raise_for_status()

                initial_balance = int(start_game.json().get('clickerUser').get('balanceCoins'))
                print(f"ℹ️  {YELLOW}{localized_text('balance')}: {LIGHT_MAGENTA}{initial_balance:,}{WHITE}".replace(',', ' '))

                current_balance = int(self._sync().get('balanceCoins'))
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                print(f"ℹ️  {YELLOW}{localized_text('balance')}: {balance} | {localized_text('passive')}".replace(',', ' '))

                cipher = self._get_mini_game_cipher(minigame)
                json_data = {'cipher': cipher, 'miniGameId': game_id}
                end_game = requests.post(f'{self.base_url}/clicker/claim-daily-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                end_game.raise_for_status()

                end_game_data = end_game.json()
                current_balance = int(self._sync().get('balanceCoins'))
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                bonus = f"{LIGHT_BLUE}+{int(end_game_data.get('bonus')):,}{WHITE}"
                print(f"ℹ️  {YELLOW}{localized_text('balance')}: {balance} [{bonus}] | {localized_text('passive_and_bonus')}\n".replace(',', ' '))

                if bonus_keys == 0:
                    print(f"✅  {localized_text('info_minigame_complete', game_id)}. {next_minigame}")
                else:
                    print(f"✅  {localized_text('info_minigame_complete_2', game_id)}: {bonus_keys}")

            else:
                print(f"ℹ️  {localized_text('info_minigame_already_completed', game_id)}")

        except requests.exceptions.HTTPError as e:
            if end_game.json().get('error_code') == 'DAILY_KEYS_MINI_GAME_WRONG':
                print(f"🚫  {localized_text('error_wrong_minigame_cipher', game_id)}")

            elif start_game.json().get('error_code') == 'KEYS-MINIGAME_WAITING':
                print(f"🚫  {localized_text('error_next_minigame_attempt')}: {next_attempt}")

            else:
                print(f"🚫  {localized_text('error_occured')}: {e}")
                logging.error(traceback.format_exc())

    def send_balance_to_group(self, update_time_sec=7200, chat_id=None):
        try:
            while True:
                info = self._get_balance()
                user_id = self._get_telegram_user_id()

                update_date = datetime.fromtimestamp(info['date']).strftime('%Y-%m-%d %H:%M:%S')
                result = f"💰  Баланс: {info['balanceCoins']:,} \n" \
                         f"⭐️  Всего: {info['total']:,} \n" \
                         f"🆔  ID пользователя: {user_id} \n" \
                         f"🔄  Обновление: {update_date}"
                balance = result.replace(',', ' ')

                if chat_id is not None:
                    response = requests.post(f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage", data={"chat_id": int(chat_id), "text": balance})
                    response.raise_for_status()
                else:
                    response = requests.post(f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage", data={"chat_id": int(self.CHAT_ID), "text": balance})
                    response.raise_for_status()

                print(f"✅  {update_date} · Баланс успешно отправлен в группу")
                time.sleep(update_time_sec)

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

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
                        remain = f"{LIGHT_MAGENTA}{remain_time(state['receiveKeysRefreshSec'])}{WHITE}"
                        next_keys = f"{localized_text('info_next_keys_after')}: {remain}"
                except:
                    keys_today = 0

            promos = response.json()['promos']
            for promo in promos:
                if promo['promoId'] == promo_id:
                    keys_limit = promo['keysPerDay']
                    promo_title = promo['title']['en']

            if keys_today == keys_limit:
                print(f"ℹ️  {localized_text('info_all_keys_in_game_claimed', promo_title)}. {next_keys}")

            else:
                print(f"ℹ️  {LIGHT_YELLOW}🔄  {localized_text('info_activating_promocode')} `{promoCode}`...{WHITE}")

                time.sleep(2)
                json_data = {'promoCode': promoCode}
                response = requests.post(f'{self.base_url}/clicker/apply-promo', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
                response.raise_for_status()

                reward = response.json()['reward']
                if reward['type'] == 'keys':
                    print(f"ℹ️  {LIGHT_GREEN}🎉  {localized_text('info_keys_recieved')}: {keys_today + reward['amount']}/{keys_limit} {WHITE}\n")

                elif reward['type'] == 'coins':
                    print(f"ℹ️  {LIGHT_GREEN}🎉  {localized_text('info_coins_recieved')}: {reward['coins']:,}{WHITE}\n".replace(',', ' '))

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def evaluate_cards(self) -> list:
        response = requests.post(f'{self.base_url}/clicker/upgrades-for-buy', headers=self._get_headers(self.HAMSTER_TOKEN))
        response.raise_for_status()

        evaluated_cards = []
        upgrades = response.json()['upgradesForBuy']
        for card in upgrades:
            cooldown = card.get('cooldownSeconds', 1)
            if card['isAvailable'] and not card['isExpired'] and cooldown == 0:
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
        return sorted_cards[:config.cards_in_top]

    def get_account_info(self):
        try:
            response = requests.post(f'{self.base_url}/auth/account-info', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            account_info = response.json()['accountInfo']['telegramUsers'][0]
            return account_info

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

    def get_cooldowns(self) -> dict:
        def _post_request(endpoint):
            response = requests.post(f'{self.base_url}/{endpoint}', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()
            return response.json()

        result = {}

        try:
            # Fetch config data
            config_data = _post_request('clicker/config')
            result['cipher'] = {
                'remain': int(config_data['dailyCipher'].get('remainSeconds', 0)),
                'completed': config_data['dailyCipher'].get('isClaimed', False)
            }
            result['minigames'] = [
                {
                    'name': game_id,
                    'remain': int(data.get('remainSeconds', 0)),
                    'completed': data.get('isClaimed', False)
                }
                for game_id, data in config_data.get('dailyKeysMiniGames', {}).items()
            ]

            # Fetch upgrades data
            upgrades_data = _post_request('clicker/upgrades-for-buy')
            result['combo'] = {
                'remain': int(upgrades_data['dailyCombo'].get('remainSeconds', 0)),
                'completed': upgrades_data['dailyCombo'].get('isClaimed', False)
            }

            # Fetch tasks data
            tasks_data = _post_request('clicker/list-tasks')
            result['tasks'] = {
                'remain': int(next((task.get('remainSeconds', 0) for task in tasks_data.get('tasks', []) if task['id'] == 'streak_days_special'), 0)),
                'completed': next((task.get('isCompleted', False) for task in tasks_data.get('tasks', []) if task['id'] == 'streak_days_special'), False)
            }

            # Fetch taps data
            taps_data = _post_request('clicker/sync').get('clickerUser', {})
            max_taps = int(taps_data.get('maxTaps', 0))
            taps_per_sec = int(taps_data.get('tapsRecoverPerSec', 0))
            available_taps = int(taps_data.get('availableTaps', 0))
            result['taps'] = {
                'remain': int(max_taps / taps_per_sec) + 10,
                'completed': available_taps != max_taps
            }

            # Fetch promos data
            promo_response = _post_request('clicker/get-promos')
            promos = promo_response.get('promos', [])
            states = promo_response.get('states', [])
            promo_results = [
                {
                    'name': promo['title']['en'],
                    'remain': int(state.get('receiveKeysRefreshSec', 0)),
                    'completed': state.get('receiveKeysToday', 0) == promo['keysPerDay']
                }
                for promo in promos
                for state in states
                if promo['promoId'] == state['promoId']
            ]
            result['promos'] = promo_results

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())

        return result

    def bonus_for_one_point(self, mini_game: dict) -> int:
        json_data = {'miniGameId': mini_game.get('id')}
        requests.post(f'{self.base_url}/clicker/start-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)

        cipher = self._get_mini_game_cipher(mini_game, one_point=True)
        json_data = {'cipher': cipher, 'miniGameId': mini_game.get('id')}
        end_game = requests.post(f'{self.base_url}/clicker/claim-daily-keys-minigame', headers=self._get_headers(self.HAMSTER_TOKEN), json=json_data)
        bonus = int(end_game.json().get('bonus'))
        return bonus

    def login(self):
        try:
            response = requests.post(f'{self.base_url}/auth/account-info', headers=self._get_headers(self.HAMSTER_TOKEN))
            if response.status_code == 401:
                print(f"🚫  {localized_text('error_occured')}: 401 Unauthorized. Сheck your `{config.account}` for correct")
                exit(1)

            else:
                data = response.json()
                account_info = data['accountInfo']['telegramUsers'][0]
                username = account_info.get('username', 'n/a')
                first_name = account_info.get('firstName', 'n/a')
                last_name = account_info.get('lastName', 'n/a')
                config.hamster_token = True

                print(f"{DARK_GRAY}ℹ️  {localized_text('sign_in')} {first_name} {last_name} ({username}){WHITE}\n")

        except Exception as e:
            try:
                error = data.get('error_code')
                if error:
                    if error['error_code'] == 'BAD_AUTH_TOKEN':
                        print(f"{RED}🚫  {localized_text('error_occured')}: {data['error_code']}\n"
                              f"    {localized_text('error_hamster_token_not_specified')}{WHITE}")
                    else:
                        print(f"{RED}🚫  {localized_text('error_occured')}: {data['error_code']}{WHITE}")
                        logging.error(traceback.format_exc())
            except:
                pass

            config.hamster_token = False
            print(f"{RED}❌  {localized_text('error_hamster_token_not_specified')}{WHITE}")
            print(f"{YELLOW}⚠️ {localized_text('warning_hamster_combat_unavailable')}{WHITE}")
            logging.error(e)

    def get_purhase_count(self):
        result = {}
        try:
            response = requests.post(f'{self.base_url}/clicker/sync', headers=self._get_headers(self.HAMSTER_TOKEN))
            response.raise_for_status()

            upgrades = response.json().get('clickerUser').get('upgrades')
            result = {
                'upgrades_count': sum(item["level"] for item in upgrades.values()),
                'cards_count': sum(1 for item in upgrades.values() if item["level"] > 0)
            }
            return result

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return result

    async def get_promocodes(self, count=1, send_to_group=None, apply_promo=False, prefix=None, save_to_file=None, one_game=None):
        games_data = [app for app in get_games_data()['apps'] if app.get('available')]

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

        async def __get_client_token(session, client_id: str) -> str:
            client_token = ''
            url = 'https://api.gamepromo.io/promo/login-client'
            headers = {'Content-Type': 'application/json'}
            payload = {'appToken': APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    response.raise_for_status()

                    data = await response.json()
                    client_token = data.get('clientToken')
                    return client_token

            except Exception as e:
                print(f"🚫  {localized_text('error_occured')}: {e}")
                return client_token

        async def __emulate_progress(session, client_token: str) -> str:
            has_code = ''
            url = 'https://api.gamepromo.io/promo/register-event'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    response.raise_for_status()

                    has_code = data.get('hasCode')
                    return has_code

            except Exception as e:
                print(f"🚫  {localized_text('error_occured')}: {e}")
                return has_code

        async def __get_promocode(session, client_token: str) -> str | None:
            promo_code = ''
            url = 'https://api.gamepromo.io/promo/create-code'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID}

            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()

                    response.raise_for_status()
                    promo_code = data.get('promoCode')
                    return promo_code

            except Exception as e:
                print(f"\n🚫  {localized_text('error_occured')}: {e}")
                return promo_code

        async def __key_generation(session, index: int, keys_count: int, progress_increment=None, progress_dict=None):
            global total_progress
            promo_code = ''
            client_id = await __generate_client_id()
            client_token = await __get_client_token(session, client_id)
            time.sleep(1)

            try:
                if progress_dict:
                    progress_dict[prefix] = f"{LIGHT_BLUE}{prefix.upper()}{WHITE} · {localized_text('status')}: {localized_text('processing')}"

                for n in range(EVENTS_COUNT):
                    await asyncio.sleep(EVENTS_DELAY * await delay_random() / 1000)
                    has_code = await __emulate_progress(session, client_token)

                    if progress_dict:
                        total_progress[prefix] += progress_increment
                        overall_progress = (total_progress[prefix] / (keys_count * EVENTS_COUNT)) * 100
                        progress_dict[prefix] = f"{LIGHT_BLUE}{prefix.upper()}{WHITE} · {localized_text('status')}: {overall_progress:.0f}%"
                    else:
                        progress_message = (n + 1) / EVENTS_COUNT * 100
                        print(f"ℹ️  {LIGHT_BLUE}{prefix}{WHITE} [{index}/{keys_count}] · {localized_text('status')}: {progress_message:.0f}%")

                    if has_code:
                        break

                promo_code = await __get_promocode(session, client_token)
                status_message = f"{LIGHT_BLUE}{prefix:<3}{WHITE} [{index}/{keys_count}] · {localized_text('status')}: {generation_status(promo_code)}"
                print(f"\r{status_message}", flush=True)
                return promo_code

            except Exception as e:
                logging.error(f"{LIGHT_RED}🚫  {prefix.upper()}{WHITE} [{index}/{keys_count}] · {localized_text('error_occured')}: {e}")
                return promo_code

        async def __start_generate(keys_count: int) -> list:
            remain = f"{LIGHT_MAGENTA}{remain_time((EVENTS_COUNT * EVENTS_DELAY) / 1000)}{WHITE}"
            print(f"\n{LIGHT_YELLOW}{TITLE} · {localized_text('generating_promocodes')}: {keys_count}{WHITE} ~ {remain}")
            print(f'{YELLOW}{TEXT}{WHITE}')

            try:
                if one_game:
                    global total_progress
                    total_progress = {prefix: 0}
                    progress_increment = 1
                    progress_dict = {prefix: ""}

                    loading_event = asyncio.Event()
                    spinner_task = asyncio.create_task(update_spinner(loading_event, progress_dict, prefix))
                    async with aiohttp.ClientSession() as session:
                        tasks = [__key_generation(session, i + 1, keys_count, progress_increment, progress_dict) for i in range(keys_count)]
                        keys = await asyncio.gather(*tasks)
                        loading_event.set()
                        await spinner_task
                    return [key for key in keys if key]

                else:
                    loading_event = asyncio.Event()
                    spinner_task = asyncio.create_task(loading_v2(loading_event))
                    async with aiohttp.ClientSession() as session:
                        tasks = [__key_generation(session, i + 1, keys_count) for i in range(keys_count)]
                        keys = await asyncio.gather(*tasks)
                        loading_event.set()
                        await spinner_task
                    return [key for key in keys if key]

            except Exception as e:
                logging.error(f"🚫  {localized_text('error_occured')}: {e}")
                return []

        promocodes = await __start_generate(count)

        line_before()
        result = f"*{EMOJI} {TITLE}*\n*{localized_text('main_menu_promocodes')}: *\n"
        for promocode in promocodes:
            result += f"·  `{promocode}`\n"
        formatted_text = result.replace('*', '').replace('`', '')
        print(formatted_text.strip())
        line_after()

        if apply_promo:
            config.send_to_group = False
            print(f"⚠️  {LIGHT_YELLOW}{localized_text('not_sent_to_group')}{WHITE}")

            config.save_to_file = False
            print(f"⚠️  {LIGHT_YELLOW}{localized_text('not_saved_to_file')}{WHITE}\n")

            for promocode in promocodes:
                self.apply_promocode(promocode, PROMO_ID)

        if send_to_group:
            try:
                telegram_response = requests.post(f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage", data={"chat_id": self.CHAT_ID, "parse_mode": "Markdown", "text": result})
                telegram_response.raise_for_status()
                time.sleep(3)
                print(f"✅  {GREEN}{localized_text('main_menu_promocodes')} `{TITLE}` {localized_text('sent_to_group')}{WHITE}")

            except Exception as error:
                print(f"🚫  Error during request to telegram API\n{error}")
                logging.error(traceback.format_exc())

        if save_to_file:
            if not os.path.exists('generated keys'):
                os.makedirs('generated keys')

            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated keys', f'generated_keys ({TITLE}).txt')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(formatted_text.strip())
                print(f"✅  {GREEN}{localized_text('main_menu_promocodes')} `{TITLE}` {localized_text('saved_to_file')}{WHITE}\n`{file_path}`")

import asyncio
import base64
import datetime
import hashlib
import logging
import os
import platform
import random
import time
import traceback
import uuid
from datetime import datetime
from random import randint

import aiohttp
import requests

from Src.Api.Endpoints import HamsterEndpoints, ResponseData
from Src.Api.Urls import currency
from Src.Colors import *
from Src.utils import (text_to_morse, remain_time, get_games_data, line_before,
                       generation_status, get_salt, localized_text, align_daily_info,
                       align_summary, line_after, update_spinner, loading_v2, kali)
from config import app_config
from database.queries import ConfigManager, UserConfig, init_db
from database.queries import SyncORM as db

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class HamsterKombatClicker:

    def __init__(self, hamster_token):
        init_db()

        self.HAMSTER_TOKEN = hamster_token
        self.BOT_TOKEN = app_config.TELEGRAM_BOT_TOKEN
        self.CHAT_ID = app_config.CHAT_ID
        self.GROUP_URL = app_config.GROUP_URL

        self.headers = self._get_headers()
        self.user_config: UserConfig = self._get_user_config()

    def _get_headers(self) -> dict:
        return {
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://hamsterkombat.io',
            'Referer': 'https://hamsterkombat.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; RMX3630 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36',
            'accept': 'application/json',
            'authorization': self.HAMSTER_TOKEN,
            'content-type': 'application/json',
            'Sec-Ch-Ua': '"Android WebView";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"'
        }

    def _get_user_config(self):
        try:
            account_info = HamsterEndpoints.get_account_info(self.headers)
            user_id = account_info.id
            username = account_info.name

            if not db.user_exist(user_id):
                db.ADD_subscriber({'tg_user_id': user_id, 'username': username})

            config_manager = ConfigManager()
            user_config = config_manager.get_user_config(user_id)

            user_config.has_hamster_token = True
            user_config.user_name = username
            user_config.tg_user_id = user_id
            return user_config

        except Exception as e:
            user_config.has_hamster_token = False
            logging.error(f"🚫  {localized_text('error_occured')}: {e}")
            exit(1)

    def login(self):
        print(f"{DARK_GRAY}ℹ️  {localized_text('sign_in')} {self.user_config.user_name} ({self.user_config.tg_user_id}) {WHITE}")

    def _get_balance(self) -> dict or None:
        result = {}
        try:
            user = HamsterEndpoints.get_user(self.headers).to_dict()
            result = {
                'balance': int(user.get(f'balance{currency}', 0)),
                'total': int(user.get(f'total{currency}', 0)),
                'keys': int(user.get(f'balanceKeys', 0)),
                'date': int(user.get('lastSyncUpdate', 0)),
                'earn_per_hour': int(user.get('earnPassivePerHour', 0))}
            return result

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return result

    def _get_mini_game_cipher(self, minigame: ResponseData, one_point=False) -> str:
        minigame_cipher = ''
        try:
            if one_point:
                max_points = 1
            else:
                max_points = minigame.maxPoints

            mini_game_id = minigame.id
            start_date = minigame.startDate
            user_id = HamsterEndpoints.get_user(self.headers).id

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
            return minigame_cipher

    def _buy_upgrade(self, upgrade_id: str) -> dict or None:
        try:
            balance = self._get_balance()
            earn_per_hour = balance.get('earn_per_hour', 0)
            free_balance = balance.get('balance') - self.user_config.balance_threshold
            if self.user_config.balance_threshold == 0:
                max_price_limit = 0
            else:
                max_price_limit = max(earn_per_hour, 50000) * 24

            upgrades = HamsterEndpoints.get_upgrades(self.headers)
            for upgrade in upgrades:
                if upgrade_id == upgrade.id:
                    price = int(upgrade.price)
                    if int(free_balance * 0.8) >= price and (max_price_limit == 0 or price < int(max_price_limit)):
                        if upgrade.isAvailable and not upgrade.isExpired and upgrade.cooldownSeconds == 0:
                            buy_upgrade_response = HamsterEndpoints.buy_upgrade(self.headers, upgrade_id)
                            if buy_upgrade_response.error_code == 'UPGRADE_MAX_LEVEL':
                                print(f"{LIGHT_YELLOW}⚠️  {localized_text('error_failed_upgrade_card')} `{upgrade.name}` {WHITE}")
                                break
                            else:
                                print(f"{GREEN}✅  {localized_text('info_card_upgraded', upgrade.name, upgrade.level + 1)}{WHITE}")

                        elif upgrade.isAvailable and upgrade.isExpired and upgrade.cooldownSeconds != 0:
                            logging.error(f"🚫  {localized_text('error_upgrade_not_avaialble_time_expired', upgrade.name)}")

                        else:
                            buy_upgrade_response = HamsterEndpoints.buy_upgrade(self.headers, upgrade_id)
                            error_message = buy_upgrade_response.error_message
                            print(f"{LIGHT_RED}🚫  {localized_text('error_upgrade_not_avaialble')} `{upgrade.name}`. {error_message}{WHITE}")
                            return error_message

                    else:
                        print(f"{RED}🚫  {localized_text('not_enough_coins')}{WHITE}")
                        break

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            print(traceback.format_exc())
            return

    def _collect_upgrades_info(self) -> dict or None:
        try:
            cipher = HamsterEndpoints.get_config(self.headers, 'cipher').cipher
            combo = HamsterEndpoints.get_combo()
            daily_combo: list = combo.combo

            total_price, total_profit, cards, cards_info = 0, 0, [], ''
            upgrades_for_buy = HamsterEndpoints.get_upgrades(self.headers)
            for upgradeId in daily_combo:
                for upgrade in upgrades_for_buy:
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
            return {'cards': cards, 'summary': summary, 'cipher': cipher, 'combo_date': combo.date}

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return

    def daily_info(self) -> str or None:
        try:
            upgrades_info = self._collect_upgrades_info()
            balance = self._get_balance()

            upgrades = HamsterEndpoints.get_user(self.headers).upgrades
            purhase_upgrades_count = sum(item["level"] for item in upgrades.values()),
            purhase_cards_count = sum(1 for item in upgrades.values() if item["level"] > 0)

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
            info += f"💰  {LIGHT_YELLOW}{align_daily_info(localized_text('balance'))}{WHITE}{balance[f'balance{currency}']:,}\n"
            info += f"💰  {LIGHT_YELLOW}{align_daily_info(localized_text('total'))}{WHITE}{balance['total']:,}\n"
            info += f"🔑  {LIGHT_YELLOW}{align_daily_info(localized_text('keys'))}{WHITE}{balance['keys']:,}\n"
            info += f"🔥  {LIGHT_YELLOW}{align_daily_info(localized_text('total_purhased_cards_count'))}{WHITE}{purhase_upgrades_count}\n"
            info += f"🔥  {LIGHT_YELLOW}{align_daily_info(localized_text('total_purhased_upgraqdes_count'))}{WHITE}{purhase_cards_count}"
            if '🚫' in result['combo']:
                info += f"\n\n⚠️  {localized_text('no_combo_today')}".replace(',', ' ')
            return info.replace(',', ' ')

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return

    def complete_taps(self):
        remain = 0
        try:
            user = HamsterEndpoints.get_user(self.headers)
            if user:
                available_taps = int(getattr(user, 'availableTaps', 0))
                max_taps = int(getattr(user, 'maxTaps', 0))
                earn_per_sec = int(getattr(user, 'earnPerTap', 0))
                taps_recoverper_sec = int(getattr(user, 'tapsRecoverPerSec', 0))

            total_remain_time = max_taps / taps_recoverper_sec
            current_remain_time = available_taps / taps_recoverper_sec
            remain = int(total_remain_time - current_remain_time)

            if available_taps == max_taps:
                count = int(max_taps / earn_per_sec)
                available_taps = int(max_taps - (count * earn_per_sec))
                HamsterEndpoints.tap(self.headers, available_taps, count)
                print(f"{GREEN}✅  {localized_text('info_taps_completed')}{WHITE}")

            else:
                print(f"{RED}🚫  {localized_text('info_no_accumulate_yet')}{WHITE}")

            boostsForBuy = HamsterEndpoints.get_boosts(self.headers)
            for boost in boostsForBuy:
                if boost.id == 'BoostFullAvailableTaps':
                    boost_remain = int(boost.cooldownSeconds)
                    count = int(max_taps / earn_per_sec)

                    if boost_remain == 0:
                        HamsterEndpoints.buy_boost(self.headers, boost.id)
                        print(f"{GREEN}✅  {localized_text('info_boost_used')}{WHITE}")

                        HamsterEndpoints.tap(self.headers, available_taps, count)
                        print(f"{GREEN}✅  {localized_text('info_taps_completed')}{WHITE}")

                    else:
                        print(f"{RED}🚫  {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} {localized_text('boosts_available')}. {localized_text('info_next_boost_after')}: {remain_time(boost_remain)}{WHITE}")

            if remain == 0:
                return int(total_remain_time)
            else:
                return remain

        except Exception as e:
            print(f"{RED}🚫  {localized_text('error_occured')}: {e}{WHITE}")

        return remain

    def complete_daily_tasks(self) -> int or None:
        remain = 0
        try:
            task_list = HamsterEndpoints.get_tasks(self.headers)
            any_completed = False

            for task in task_list:
                if task.id == 'streak_days_special':
                    remain = task.remainSeconds

                if not task.isCompleted and not task.id.startswith('invite_friends'):
                    HamsterEndpoints.check_task(self.headers, task.id)
                    print(f"{LIGHT_YELLOW}⭐️  {localized_text('info_task_completed', task.id)}{WHITE}")
                    any_completed = True

            if any_completed:
                print(f"{GREEN}✅  {localized_text('info_all_tasks_complete')}{WHITE}")

            else:
                print(f"{YELLOW}ℹ️  {localized_text('info_all_tasks_already_complete')}{WHITE}")
            return remain

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return remain

    def complete_daily_chipher(self) -> int or None:
        remain = 0
        try:
            daily_cipher = HamsterEndpoints.get_config(self.headers, key='cipher')
            remain = daily_cipher.remainSeconds

            if not daily_cipher.isClaimed:
                encoded_cipher = HamsterEndpoints.get_config(self.headers, 'cipher').cipher
                cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
                HamsterEndpoints.claim_cipher(self.headers, cipher)
                print(f"{GREEN}✅  {localized_text('info_cipher_completed')}{WHITE}")

            else:
                print(f"{YELLOW}ℹ️  {localized_text('info_cipher_already_complete')}{WHITE}")

            return remain

        except Exception as e:
            print(f"{RED}🚫  {localized_text('error_occured')}: {e}{WHITE}")
            return remain

    def complete_daily_combo(self, buy_anyway=False) -> int or None:
        remain = 0
        try:
            upgrades = HamsterEndpoints.get_upgrades(self.headers)
            combo = upgrades.dailyCombo

            balance = self._get_balance()
            earn_per_hour = balance.get('earn_per_hour')
            free_balance = balance.get(f'balance{currency}') - self.user_config.balance_threshold

            already_purchased_cards = set(combo.upgradeIds)
            remain = combo.remainSeconds

            cards = set(HamsterEndpoints.get_combo().combo)

            cards_for_buy = list(cards - already_purchased_cards)
            cards_for_buy_names = ', '.join(cards_for_buy)

            is_claimed = combo.get('isClaimed')
            if not is_claimed:
                if not buy_anyway:
                    print(f"{LIGHT_YELLOW}⚠️  {localized_text('not_all_carda_available')}\n⭐️  {YELLOW}{cards_for_buy_names}{WHITE}")
                    choice = input(kali(localized_text('yes_enter'), '~/Buy combo', localized_text('continue')))
                    if choice.lower() != 'y' or choice == '':
                        print(f"\n{LIGHT_YELLOW}🚫  {localized_text('combo_cancel')}{WHITE}\n")
                        return

                for card in cards_for_buy:
                    for upgrade in upgrades:
                        card_id = card.lower().strip()
                        upgrade_id = upgrade.get('id').lower().strip()

                        if card_id == upgrade_id:
                            price = int(upgrade.price)
                            max_price_limit = max(earn_per_hour, 50000) * 24

                            if int(free_balance * 0.8) >= price and price < int(max_price_limit):
                                print(f"{YELLOW}ℹ️  {localized_text('bying_upgrade', upgrade.id, price)} {WHITE}")
                                self._buy_upgrade(upgrade.id)

                HamsterEndpoints.claim_combo(self.headers)
                print(f"\n{GREEN}✅  {localized_text('info_combo_completed')}{WHITE}")

            else:
                print(f"{YELLOW}ℹ️  {localized_text('info_combo_already_complete')}{WHITE}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return remain

    def complete_daily_minigame(self, game_id: str) -> int or None:
        remain = 0
        try:
            minigames = HamsterEndpoints.get_config(self.headers, 'minigames')
            minigame = next((m for m in minigames if game_id.capitalize() == m.id), None)

            remain = int(minigame.remainSeconds)
            bonus_keys = int(minigame.bonusKeys)

            is_claimed = minigame.isClaimed
            if not is_claimed:
                if minigame.id == 'Tiles':
                    try:
                        one_point_bonus = self.bonus_for_one_point(minigame)
                        self.user_config.bonus_for_one_point = one_point_bonus
                    except:
                        one_point_bonus = self.user_config.bonus_for_one_point

                    max_currency = int(one_point_bonus * minigame.maxPoints)
                    print(f"{YELLOW}ℹ️  {localized_text('info_coinf_for_one_point')}:  {LIGHT_BLUE}{one_point_bonus}{WHITE} \n"
                          f"{YELLOW}ℹ️  {localized_text('info_max_coins')}: {LIGHT_YELLOW}{max_currency:,}{WHITE}\n".replace(',', ' '))

                HamsterEndpoints.start_minigame(self.headers, minigame.id)
                initial_balance = int(HamsterEndpoints.get_user(self.headers).balanceDiamonds)
                print(f"{YELLOW}ℹ️  {localized_text('balance')}: {LIGHT_MAGENTA}{initial_balance:,}{WHITE}".replace(',', ' '))

                current_balance = int(HamsterEndpoints.get_user(self.headers).balanceDiamonds)
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                print(f"{YELLOW}ℹ️  {localized_text('balance')}: {balance} | {localized_text('passive')}".replace(',', ' '))

                cipher = self._get_mini_game_cipher(minigame)
                end_game = HamsterEndpoints.claim_minigame(self.headers, cipher, minigame.id)

                current_balance = int(HamsterEndpoints.get_user(self.headers).balanceDiamonds)
                balance_increase = current_balance - initial_balance
                balance = f"{LIGHT_MAGENTA}{current_balance:,}{WHITE} ({LIGHT_GREEN}+{balance_increase:,}{WHITE})"
                bonus = f"{LIGHT_BLUE}+{int(end_game.bonus):,}{WHITE}"
                print(f"{YELLOW}ℹ️  {localized_text('balance')}: {balance} [{bonus}] | {localized_text('passive_and_bonus')}\n".replace(',', ' '))

                if bonus_keys == 0:
                    print(f"{GREEN}✅  {localized_text('info_minigame_complete', minigame.id)}{WHITE}")
                else:
                    print(f"{GREEN}✅  {localized_text('info_minigame_complete_2', minigame.id)}: {bonus_keys}{WHITE}")

            else:
                print(f"{YELLOW}ℹ️  {localized_text('info_minigame_already_completed', minigame.id)}{WHITE}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return remain

    def send_to_chat(self, chat_id: int = None, message: str = None, completed=None):
        try:
            mesage = f">🙍‍♂️‍  {self.user_config.user_name} \n" \
                     f">🆔  {self.user_config.tg_user_id} \n" \
                     f"*{completed}*\n" \
                     f"{message}"

            url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
            try:
                response = requests.post(url, data={"chat_id": int(chat_id), "text": mesage, "parse_mode": "MarkdownV2"})
            except:
                response = requests.post(url, data={"chat_id": int(self.CHAT_ID), "text": mesage, "parse_mode": "MarkdownV2"})
            response.raise_for_status()

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            return

    def send_balance_to_group(self, update_time_sec: int = None, chat_id: int = None):
        try:
            while True:
                balance = self._get_balance()
                user_id = HamsterEndpoints.get_user(self.headers).id

                update_date = datetime.fromtimestamp(balance['date']).strftime('%Y-%m-%d %H:%M:%S')
                result = f"🙍‍  *{self.user_config.user_name}* \n" \
                         f"🆔  `{user_id}` \n\n" \
                         f"💰  {localized_text('balance')}: *{balance[f'balance{currency}']:,}* \n" \
                         f"🌟  {localized_text('total')}: *{balance['total']:,}* \n" \
                         f"📈  {localized_text('profit')}: *{balance['earn_per_hour']:,}* \n" \
                         f"🔑  {localized_text('keys')}: *{balance['keys']:,}* \n\n" \
                         f"🔄  {update_date}"
                message = result.replace(',', ' ')

                url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
                try:
                    response = requests.post(url, data={"chat_id": int(chat_id), "text": message, "parse_mode": "Markdown"})
                except:
                    response = requests.post(url, data={"chat_id": int(self.CHAT_ID), "text": message, "parse_mode": "Markdown"})
                response.raise_for_status()

                if update_time_sec is None:
                    print(f"{GREEN}✅  {update_date} · {localized_text('balance_sended_to_chat')}{WHITE}")
                    time.sleep(7200)
                else:
                    print(f"{GREEN}✅  {localized_text('balance_sended_to_chat')}{WHITE}")
                    print(f"\n{balance}\n")
                    return update_time_sec

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")

    def apply_promocode(self, promocode, promo_id):
        try:
            promos = HamsterEndpoints.get_promos(self.headers)

            keys_today = 0
            keys_limit = 1
            for promo in promos:
                if promo.promo_id == promo_id:
                    try:
                        keys_today = promo.keys
                        keys_limit = promo.per_day
                        remain = f"{LIGHT_MAGENTA}{remain_time(int(promo.seconds))}{WHITE}"
                        next_keys = f"{localized_text('info_next_keys_after')}: {remain}"
                    except:
                        keys_today = 0

            if keys_today == keys_limit:
                print(f"{LIGHT_YELLOW}ℹ️  {localized_text('info_all_keys_in_game_claimed', promo.name)}. {next_keys}{WHITE}")

            else:
                print(f"{LIGHT_YELLOW}🔄  {localized_text('info_activating_promocode')}: {promocode}...{WHITE}")

                time.sleep(2)
                reward = HamsterEndpoints.apply_promo(self.headers, promocode)
                if reward.type == currency.lower():
                    print(f"{LIGHT_GREEN}💎  {localized_text('info_currency_recieved', reward.type.title())}: {keys_today + reward.amount}/{keys_limit} {WHITE}\n")
                elif reward.type == 'coins':
                    print(f"{LIGHT_GREEN}🪙  {localized_text('info_currency_recieved', reward.type.title())}: {reward.amount:,}{WHITE}\n".replace(',', ' '))
                elif reward.type == 'keys':
                    print(f"{LIGHT_GREEN}🔑  {localized_text('info_currency_recieved', reward.type.title())}: {reward.amount:,}{WHITE}\n".replace(',', ' '))
                else:
                    print(f"{LIGHT_GREEN}🎉  {localized_text('info_currency_recieved', reward.type.title())}: {reward.amount:,}{WHITE}\n".replace(',', ' '))
            print()

        except Exception as e:
            logging.error(f"🚫  {localized_text('error_occured')}: {e}")

    def get_most_profitable_cards(self, top=False) -> list:
        evaluated_cards = []
        try:
            upgrades = HamsterEndpoints.get_upgrades(self.headers)
            for card in upgrades:
                card = card.to_dict()
                cooldown = card.get('cooldownSeconds', 0)
                card["remain"] = int(cooldown)

                if card['isAvailable'] and not card['isExpired'] and (cooldown == 0 or self.user_config.all_cards_in_top):
                    expired_at = card.get('expiresAt', None)
                    if expired_at:
                        date_time = datetime.strptime(card['expiresAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        current_time = datetime.now()
                        time_left = date_time - current_time
                        card["expired_at"] = remain_time(int(time_left.total_seconds()))
                    else:
                        card["expired_at"] = None

                    if card["profitPerHourDelta"] != 0:
                        payback_seconds = card["price"] / card["profitPerHour"] * 3600
                        card["payback_period"] = remain_time(payback_seconds)
                        card["payback_days"] = f"{payback_seconds / 86400:.0f}"
                        card["profitability_ratio"] = 100 if card["price"] == 0 else (card["profitPerHour"] / card["price"]) * 100
                    else:
                        card["payback_period"] = float('inf')
                        card["profitability_ratio"] = 0
                    evaluated_cards.append(card)

            sorted_cards = sorted(evaluated_cards, key=lambda x: x["profitability_ratio"], reverse=True)
            if top:
                return [card.get('id') for card in sorted_cards[:top]]

            else:
                return sorted_cards[:self.user_config.cards_in_top]

        except Exception as e:
            logging.error(f"🚫  {localized_text('error_occured')}: {e}")

    def get_cooldowns(self) -> dict:
        result = {}

        try:
            # Fetch cipher data
            config_data = HamsterEndpoints.get_config(self.headers).to_dict()
            # result['cipher'] = {
            #     'remain': int(config_data.get('dailyCipher', {}).get('remainSeconds', 0)),
            #     'completed': config_data.get('dailyCipher', {}).get('isClaimed', False)}

            result['minigames'] = [{
                'name': game_id,
                'remain': int(data.get('remainSeconds', 0)),
                'completed': data.get('isClaimed', False)}
                for game_id, data in config_data.get('dailyKeysMiniGames', {}).items()]

            # # Fetch combo
            # upgrades_data = HamsterEndpoints.get_upgrades(self.headers)
            # print(upgrades_data)
            # result['combo'] = {
            #     'remain': int(upgrades_data.get('dailyCombo', {}).get('remainSeconds', 0)),
            #     'completed': upgrades_data.get('dailyCombo', {}).get('isClaimed', False)
            # }

            # Fetch tasks data
            tasks_data = HamsterEndpoints.get_tasks(self.headers)
            result['tasks'] = {
                'remain': int(next((getattr(task, 'remainSeconds', 0) for task in tasks_data if task.id == 'streak_days_special'), 0)),
                'completed': next((getattr(task, 'isCompleted', False) for task in tasks_data if task.id == 'streak_days_special'), False)
            }

            # Fetch taps data
            taps_data = HamsterEndpoints.get_user(self.headers)
            available_taps = int(getattr(taps_data, 'availableTaps', 0))
            max_taps = int(getattr(taps_data, 'maxTaps', 0))
            taps_per_sec = int(getattr(taps_data, 'tapsRecoverPerSec', 0))
            try:
                current_remain_time = int(available_taps / taps_per_sec)
                total_remain_time = int(max_taps / taps_per_sec)
                taps_remain = remain_time(int(total_remain_time - current_remain_time))
                remain = int(max_taps / taps_per_sec)
            except ZeroDivisionError:
                taps_remain = 'n/a'
                remain = 'n/a'

            result['taps'] = {
                'remain': remain,
                'completed': available_taps != max_taps,
                'taps_remain': taps_remain
            }

            # Fetch promos data
            promos = HamsterEndpoints.get_promos(self.headers)
            result['promos'] = [{
                'name': promo.name,
                'remain': int(promo.seconds),
                'completed': promo.keys == promo.per_day}
                for promo in promos]

            return result

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return result

    def bonus_for_one_point(self, minigame: ResponseData) -> int:
        HamsterEndpoints.start_minigame(self.headers, minigame.id)
        cipher = self._get_mini_game_cipher(minigame, one_point=True)
        bonus = HamsterEndpoints.claim_minigame(self.headers, cipher, minigame.id).bonus
        return bonus

    def minigames_for_generate(self) -> tuple:
        result, remain = [], 0
        try:
            games_data = get_games_data()
            promos = HamsterEndpoints.get_promos(self.headers)

            remain = promos[0].seconds
            for game in games_data:
                prefix = game.get('prefix', 'n/a')
                promo = next((p for p in promos if p.name == game['title']), None)

                if promo:
                    is_claimed = promo.is_claimed
                    recieved_keys = promo.keys
                    keys_per_day = promo.per_day
                    count = int(keys_per_day - recieved_keys)
                    promo_name = promo.name
                else:
                    is_claimed = False
                    recieved_keys = 0
                    keys_per_day = 1
                    count = int(keys_per_day - recieved_keys)
                    promo_name = game['title']

                if not is_claimed:
                    result.append({'prefix': prefix, 'count': count})
                else:
                    promo = f"{LIGHT_YELLOW}`{promo_name}`{WHITE}"
                    print(f"{YELLOW}ℹ️  {localized_text('info_all_promo_for_game_recieved', promo)}{WHITE}")

            if not result:
                print(f"{YELLOW}ℹ️  {localized_text('info_all_promocodes_already_recieved')}{WHITE}")

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")

        return result, remain

    async def get_promocodes(self, count=1, send_to_group=False, apply_promo=False, prefix=None, save_to_file=None, one_game=None):
        games_data = get_games_data()

        for promo in games_data:
            if promo['prefix'] == prefix:
                APP_TOKEN = promo['appToken']
                PROMO_ID = promo['promoId']
                EVENTS_DELAY = promo['registerEventTimeout']
                EVENTS_COUNT = promo['eventsCount']
                TITLE = promo['title']
                EMOJI = promo['emoji']

        async def delay_random():
            return random.random() / 3 + 1

        async def __generate_client_id() -> str:
            timestamp = int(time.time() * 1000)
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
            return f"{timestamp}-{random_numbers}"

        async def __get_client_token(session, client_id: str) -> str:
            client_token = ''
            login_client = 'https://api.gamepromo.io/promo/login-client'
            headers = {'Content-Type': 'application/json'}
            payload = {'appToken': APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

            try:
                async with session.post(login_client, json=payload, headers=headers) as response:
                    response.raise_for_status()

                    data = await response.json()
                    client_token = data.get('clientToken')
                    return client_token

            except Exception as e:
                logging.error(f"🚫  {localized_text('error_occured')}: {e}")
                return client_token

        async def __emulate_progress(session, client_token: str) -> str:
            has_code = ''
            register_event_url = 'https://api.gamepromo.io/promo/register-event'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

            try:
                async with session.post(register_event_url, json=payload, headers=headers) as response:
                    data = await response.json()
                    response.raise_for_status()

                    has_code = data.get('hasCode')
                    return has_code

            except Exception as e:
                logging.error(f"🚫  {localized_text('error_occured')}: {e}")
                return has_code

        async def __get_promocode(session, client_token: str) -> str:
            promo_code = ''
            create_code_url = 'https://api.gamepromo.io/promo/create-code'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {client_token}'}
            payload = {'promoId': PROMO_ID}

            try:
                async with session.post(create_code_url, json=payload, headers=headers) as response:
                    data = await response.json()

                    response.raise_for_status()
                    promo_code = data.get('promoCode')
                    return promo_code

            except Exception as e:
                logging.error(f"🚫  {localized_text('error_occured')}: {e}")
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
                        print(f"{LIGHT_BLUE}{prefix}{WHITE} [{index}/{keys_count}] · {localized_text('status')}: {progress_message:.0f}%")

                    if has_code:
                        break

                promo_code = await __get_promocode(session, client_token)
                status_message = f"{LIGHT_BLUE}{prefix.ljust(5)}{WHITE} [{index}/{keys_count}] · {localized_text('status')}: {generation_status(promo_code)}"
                print(f"\r{status_message}", flush=True)
                return promo_code

            except Exception as e:
                logging.error(f"{LIGHT_RED}🚫  {prefix.upper()}{WHITE} [{index}/{keys_count}] · {localized_text('error_occured')}: {e}")
                return promo_code

        async def __start_generate(keys_count: int) -> list:
            remain = f"{remain_time((EVENTS_COUNT * EVENTS_DELAY) / 1000)}"
            print(f"{LIGHT_YELLOW}{EMOJI}  {TITLE} · {localized_text('generating_promocodes')}: {keys_count}{WHITE} ~{remain}")

            try:
                if one_game:
                    global total_progress
                    total_progress = {prefix: 0}
                    progress_increment = 1
                    progress_dict = {prefix: ""}

                    loading_event = asyncio.Event()
                    spinner_task = asyncio.create_task(update_spinner(self.user_config.spinner, loading_event, progress_dict, prefix))
                    async with aiohttp.ClientSession() as session:
                        tasks = [__key_generation(session, i + 1, keys_count, progress_increment, progress_dict) for i in range(keys_count)]
                        keys = await asyncio.gather(*tasks)
                        loading_event.set()
                        await spinner_task
                    return [key for key in keys if key]

                else:
                    loading_event = asyncio.Event()
                    spinner_task = asyncio.create_task(loading_v2(self.user_config.spinner, loading_event))
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
            self.user_config.send_to_group = False
            # print(f"⚠️  {localized_text('not_sent_to_group')}")

            self.user_config.save_to_file = False
            # print(f"⚠️  {localized_text('not_saved_to_file')}\n")

            for promocode in promocodes:
                self.apply_promocode(promocode, PROMO_ID)

        if send_to_group:
            try:
                url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
                json_data = {"chat_id": self.CHAT_ID, "parse_mode": "Markdown", "text": result}
                telegram_response = requests.post(url, data=json_data)
                telegram_response.raise_for_status()
                time.sleep(3)
                print(f"✅  {GREEN}{localized_text('main_menu_promocodes')} {LIGHT_YELLOW}`{TITLE}`{GREEN} {localized_text('sent_to_group')}{WHITE}")

            except Exception as error:
                print(f"🚫  Error during request to telegram API")
                logging.error(f"\n{error}\n{traceback.format_exc()}")

        if save_to_file:
            if not os.path.exists('generated keys'):
                os.makedirs('generated keys')

            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated keys', f'generated_keys ({TITLE}).txt')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(formatted_text.strip())
                print(f"✅  {GREEN}{localized_text('main_menu_promocodes')} `{TITLE}` {localized_text('saved_to_file')}{WHITE}\n`{file_path}`")

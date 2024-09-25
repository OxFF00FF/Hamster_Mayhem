import json
import logging
import os
import time
import traceback
from urllib.parse import unquote

import requests
from fake_useragent import UserAgent
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from Src.Api.Urls import HamsterUrls, season
from Src.utils import localized_text, remain_time
from config import app_config

from Src.Colors import *


class ResponseData:
    def __init__(self, **kwargs):
        self.error_code = None
        self.remainSeconds = None
        self.isCompleted = None
        self.remainSeconds = None
        self.promo_id = None
        self.amount = None
        self.type = None
        self.bonus = None
        self.price = None
        self.isExpired = None
        self.cooldownSeconds = None
        self.isAvailable = None
        self.level = None
        self.remain = None
        self.startDate = None
        self.maxPoints = None
        self.upgrades = None
        self.error_message = None
        self.balanceDiamonds = None
        self.per_day = None
        self.keys = None
        self.is_claimed = None
        self.seconds = None
        self.totalDiamonds = None
        self.date = None
        self.name = None
        self.id = None
        self.combo = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: dict) -> 'ResponseData':
        return cls(**data)

    def to_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if value is not None}


def get_data(endpoint: str, headers: dict = None, data=None) -> dict:
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        success = response.json()
        return success

    except requests.RequestException:
        try:
            error = response.json()
            print(f"\n{RED}🚫  {localized_text('error_occured')}: {error.get('error_code')}{WHITE}")
            print(f"{YELLOW}📨  {error.get('error_message')}{WHITE}\n")
            return error

        except Exception as e:
            if response.status_code == 401:
                print(f"\n{RED}❌ 401 Unauthorized. check your hamster_token for corrcect{WHITE}\n")
                exit(1)
            elif response.status_code in [502, 503, 404, 500]:
                print(f"\n{RED}❌  {localized_text('error_hamster_dont_work')}{WHITE} · Error code: {response.status_code}{WHITE}\n")
                exit(1)
            else:
                print(f"\n{LIGHT_RED}🚫  {localized_text('error_occured')}: {e}{WHITE}")
                print(f"{RED}❌  {localized_text('error_internet_establish_connection')}{WHITE}")
                exit(1)
    except:
        print(f"{YELLOW}⚠️  {localized_text('error_network_problem')}{WHITE}\n")
        logging.error(traceback.format_exc())
        exit(1)


class HamsterEndpoints:

    @staticmethod
    async def login_by_telegram(session_name: str = 'hamster_mayhem'):
        ua = UserAgent()

        sdir = "sessions"
        if not os.path.exists(sdir):
            os.makedirs(sdir)

        try:
            id_ = app_config.TELEGRAM_API_ID
            hash_ = app_config.TELEGRAM_API_HASH
            session = session_name
            url = HamsterUrls.base_url

            async with Client(name=session, api_id=id_, api_hash=hash_, workdir=sdir) as client:
                peer = await client.resolve_peer('hamster_kombat_bot')
                web_view = await client.invoke(RequestWebView(peer=peer, bot=peer, platform='android', from_bot_menu=False, url=url))
                init_data_raw = unquote(web_view.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

            json_data = json.dumps({"initDataRaw": init_data_raw})
            headers = {
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Origin': HamsterUrls.main_url,
                'Referer': HamsterUrls.main_url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': ua.random,
                'accept': 'application/json',
                'content-type': 'application/json'
            }
            response = requests.post(url=HamsterUrls.auth_by_telegram, headers=headers, data=json_data)
            response.raise_for_status()

            data = response.json()
            if data:
                auth_token = data.get('authToken')
                return f"Bearer {auth_token}" if auth_token else None

        except Exception as e:
            logging.error(f"🚫  {RED}{localized_text('error_failed_login_with_telegram')}: {e} {WHITE}")
            exit(1)

    @staticmethod
    def get_user(headers) -> ResponseData:
        try:
            user = get_data(HamsterUrls.sync, headers).get(f'{season}User', {})
            return ResponseData.from_dict(user)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_userdata')}{WHITE}")

    @staticmethod
    def get_account_info(headers) -> ResponseData:
        try:
            account_info = get_data(HamsterUrls.account_info, headers).get('accountInfo', {})
            return ResponseData.from_dict(account_info)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_account_info')}{WHITE}")

    @staticmethod
    def get_combo() -> ResponseData:
        try:
            combo = get_data(HamsterUrls.get_combo)
            return ResponseData.from_dict(combo)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_combo_list')}{WHITE}")

    @staticmethod
    def get_config(headers, key=None) -> ResponseData or list[ResponseData]:
        try:
            config = get_data(HamsterUrls.config, headers)
            if key == 'cipher':
                return ResponseData.from_dict(config.get('dailyCipher', {}))
            elif key == 'feature':
                return ResponseData.from_dict(config.get('feature', []))
            elif key == 'minigames':
                return [ResponseData.from_dict(game) for game in config.get('dailyKeysMiniGames', []).values()]
            else:
                return ResponseData.from_dict(config)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_config')}: {key} {WHITE}")

    @staticmethod
    def get_promos(headers) -> list[ResponseData]:
        try:
            promos_data = get_data(HamsterUrls.get_promos, headers)

            promos = promos_data.get('promos', [])
            states = promos_data.get('states', [])

            result = []
            for promo in promos:
                for state in states:
                    if promo['promoId'] == state['promoId']:
                        recieved_keys = state.get('receiveKeysToday', 0)
                        keys_per_day = promo.get('keysPerDay', 0)
                        remain = int(state.get('receiveKeysRefreshSec', 0))
                        combined_item = {
                            'name': promo['title']['en'],
                            'promo_id': promo['promoId'],
                            'reward_type': promo['rewardType'],
                            'remain': remain_time(remain),
                            'keys': recieved_keys,
                            'per_day': keys_per_day,
                            'seconds': remain,
                            'is_claimed': True if recieved_keys == keys_per_day else False}
                        result.append(combined_item)
            return [ResponseData.from_dict(promo) for promo in result]

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_promos')}{WHITE}")

    @staticmethod
    def get_upgrades(headers) -> ResponseData or list[ResponseData]:
        try:
            upgrades = get_data(HamsterUrls.upgrades_for_buy, headers).get('upgradesForBuy', {})
            return [ResponseData.from_dict(upgrade) for upgrade in upgrades]

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_upgrades')}{WHITE}")

    @staticmethod
    def buy_upgrade(headers, upgrade_id) -> ResponseData:
        try:
            payload = {'upgradeId': upgrade_id, 'timestamp': int(time.time())}
            data = get_data(HamsterUrls.buy_upgrade, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_upgrade_card')}: {upgrade_id} {WHITE}")

    @staticmethod
    def tap(headers, available_taps, taps_count) -> ResponseData:
        try:
            payload = {'count': taps_count, 'availableTaps': available_taps, 'timestamp': int(time.time())}
            data = get_data(HamsterUrls.tap, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_taps')}: {taps_count}/{available_taps} {WHITE}")

    @staticmethod
    def get_boosts(headers) -> list[ResponseData]:
        try:
            boosts = get_data(HamsterUrls.boosts_for_buy, headers).get('boostsForBuy', [])
            return [ResponseData.from_dict(boost) for boost in boosts]

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_boosts')}{WHITE}")

    @staticmethod
    def buy_boost(headers, boost_id) -> ResponseData:
        try:
            payload = {'boostId': boost_id, 'timestamp': int(time.time())}
            data = get_data(HamsterUrls.buy_boost, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_buy_boost')}: {boost_id} {WHITE}")

    @staticmethod
    def get_tasks(headers) -> list[ResponseData]:
        try:
            tasks = get_data(HamsterUrls.list_tasks, headers).get('tasks', [])
            return [ResponseData.from_dict(task) for task in tasks]

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_get_tasks')}{WHITE}")

    @staticmethod
    def check_task(headers, task_id) -> ResponseData:
        try:
            payload = {'taskId': task_id}
            data = get_data(HamsterUrls.check_task, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_complete_taks')}: {task_id} {WHITE}")

    @staticmethod
    def claim_cipher(headers, cipher) -> ResponseData:
        try:
            payload = {'cipher': cipher}
            data = get_data(HamsterUrls.claim_daily_cipher, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_complete_cipher')}: {cipher} {WHITE}")

    @staticmethod
    def start_minigame(headers, minigame_id) -> ResponseData:
        try:
            payload = {'miniGameId': minigame_id}
            data = get_data(HamsterUrls.start_keys_minigame, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_start_minigame')}: {minigame_id} {WHITE}")

    @staticmethod
    def claim_minigame(headers, cipher, minigame_id) -> ResponseData:
        try:
            payload = {'cipher': cipher, 'miniGameId': minigame_id}
            data = get_data(HamsterUrls.claim_daily_keys_minigame, headers, payload)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_complete_minigame')}: {minigame_id} {WHITE}")

    @staticmethod
    def apply_promo(headers, promocode) -> ResponseData:
        try:
            payload = {'promoCode': promocode}
            data = get_data(HamsterUrls.apply_promo, headers, payload).get('reward', {})
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('error_failed_apply_promocode')}: {promocode} {WHITE}")
    
    @staticmethod
    def claim_combo(headers) -> ResponseData:
        try:
            data = get_data(HamsterUrls.apply_promo, headers)
            return ResponseData.from_dict(data)

        except:
            logging.error(f"🚫  {RED}{localized_text('')}{WHITE}")

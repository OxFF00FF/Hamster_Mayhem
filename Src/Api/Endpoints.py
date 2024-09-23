import logging
import os
import traceback
from urllib.parse import unquote

import requests
from fake_useragent import UserAgent
from pydantic import json
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from Src.Api.Urls import HamsterUrls
from Src.utils import localized_text, remain_time
from config import app_config

from Src.Colors import *


def get_data(endpoint: str, headers: dict = None) -> dict:
    try:
        response = requests.post(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return data

    except requests.RequestException:
        error = data.get('error_code')
        if error:
            if error == 'BAD_AUTH_TOKEN':
                print(f"{RED}🚫  {localized_text('error_occured')}: {data['error_code']}{WHITE}")
                print(f"{RED}🚫  {localized_text('error_hamster_token_not_specified')}{WHITE}")
                return {}
            else:
                print(f"{RED}🚫  {localized_text('error_occured')}: {data['error_code']}{WHITE}")
                return {}

        if response:
            if response.status_code == 401:
                print(f"🚫  {localized_text('error_occured')}: 401 Unauthorized. check your hamster_token for corrcect")
                exit(1)
            elif response.status_code in [502, 503, 404, 500]:
                print(f"{RED}❌  Кажется хомяк не работает!{WHITE} · Статус: {response.status_code}\n")
                exit(1)

    except Exception as e:
        print(f"🚫  {localized_text('error_occured')}: {e}")
        logging.error(traceback.format_exc())
        return {}

    except:
        logging.error(f"🚫  Не удалось установить соединение с хомяком. Проверье подключение к интеренту")
        return {}


class ResponseData:
    def __init__(self, **kwargs):
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


class HamsterEndpoints:

    @staticmethod
    async def login_by_telegram(session_name: str = 'hamster_mayhen_session'):
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
            print(f"An error occurred: {e}")
            exit(1)

    @staticmethod
    def get_user(headers) -> ResponseData:
        try:
            return ResponseData.from_dict(get_data(HamsterUrls.sync, headers).get(f'{HamsterUrls.season}User', {}))

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

    @staticmethod
    def get_account_info(headers) -> ResponseData:
        try:
            return ResponseData.from_dict(get_data(HamsterUrls.account_info, headers).get('accountInfo', {}))

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

    @staticmethod
    def get_combo() -> ResponseData:
        try:
            return ResponseData.from_dict(get_data(HamsterUrls.get_combo))

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

    @staticmethod
    def get_config(headers, key) -> ResponseData or list[ResponseData]:
        try:
            config = get_data(HamsterUrls.config, headers)

            if key == 'cipher':
                return ResponseData.from_dict(config.get('dailyCipher', {}).get('cipher', 'n/a'))

            elif key == 'feature':
                return ResponseData.from_dict(config.get('feature', []))

            elif key == 'minigames':
                return [ResponseData.from_dict(game) for game in config.get('dailyKeysMiniGames', [{}]).values()]

            else:
                return ResponseData.from_dict(config)

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

    @staticmethod
    def get_promos(headers) -> ResponseData or list[ResponseData]:
        try:
            data = get_data(HamsterUrls.get_promos, headers)
            promos = data.get('promos', [])
            states = data.get('states', [])

            result = []
            for promo in promos:
                for state in states:
                    if promo['promoId'] == state['promoId']:
                        recieved_keys = state.get('receiveKeysToday', 0)
                        keys_per_day = promo.get('keysPerDay', 0)
                        remain = int(state.get('receiveKeysRefreshSec', 0))
                        combined_item = {
                            'name': promo['title']['en'],
                            'reward_type': promo['rewardType'],
                            'remain': remain_time(remain),
                            'keys': recieved_keys,
                            'per_day': keys_per_day,
                            'seconds':remain,
                            'is_claimed': True if recieved_keys == keys_per_day else False}
                        result.append(combined_item)
            return [ResponseData.from_dict(promo) for promo in result]

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

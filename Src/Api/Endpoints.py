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
from Src.utils import localized_text
from config import app_config


def get_data(endpoint: str, headers: dict) -> dict:
    try:
        response = requests.post(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return data

    except Exception as e:
        print(f"🚫  {localized_text('error_occured')}: {e}")
        logging.error(traceback.format_exc())
        return {}


class ResponseData:
    def __init__(self, **kwargs):
        self.id = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: dict) -> 'ResponseData':
        return cls(**data)


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
            user = get_data(HamsterUrls.sync, headers).get(f'{HamsterUrls.season}User')
            if user:
                return ResponseData.from_dict(user)

        except Exception as e:
            print(f"🚫  {localized_text('error_occured')}: {e}")
            logging.error(traceback.format_exc())
            return ResponseData.from_dict({})

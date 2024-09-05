import datetime
import os
import time

import requests
from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv()


def get_headers(hamster_token: str) -> dict:
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


def send_balance_to_group():
    update_time_sec = 7200
    chat_id = int(os.getenv('CHAT_ID'))
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    hamster_token = os.getenv('HAMSTER_TOKEN')

    while True:
        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=get_headers(hamster_token))
        response.raise_for_status()

        clicker = response.json()['clickerUser']
        balance = int(clicker.get('balanceCoins', 'n/a'))
        total = int(clicker['totalCoins'])
        date = int(clicker['lastSyncUpdate'])
        user_id = int(clicker['id'])

        update_date = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
        result = f"💰  Баланс: {balance:,} \n" \
                 f"⭐️  Всего: {total:,} \n" \
                 f"🆔  ID пользователя: {user_id} \n" \
                 f"🔄  Обновление: {update_date}"
        text = result.replace(',', ' ')

        if chat_id is not None:
            response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": chat_id, "text": text})
            response.raise_for_status()
        else:
            response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": chat_id, "text": balance})
            response.raise_for_status()

        print(f"✅  {update_date} · Баланс успешно отправлен в группу")
        time.sleep(update_time_sec)


if __name__ == '__main__':
    send_balance_to_group()

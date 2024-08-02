# -*- coding: utf-8 -*-
import datetime
import os
import requests
import time
import logging

from dotenv import load_dotenv

# Read .env file
load_dotenv()

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s |  %(message)s', level=logging.INFO)

required_values = ['HAMSTER_TOKEN', 'BOT_TOKEN', 'GROUP_ID']
missing_values = [value for value in required_values if os.environ.get(value) == 'XXX']
if len(missing_values) > 0:
    logging.error(f'The following environment values are missing in your .env: {", ".join(missing_values)}')
    exit(1)


HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

HEADERS = {
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://hamsterkombat.io',
    'Referer': 'https://hamsterkombat.io/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'accept': 'application/json',
    'authorization': HAMSTER_TOKEN,
    'content-type': 'application/json',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def get_balance():
    r = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=HEADERS)
    if r.status_code != 200:
        logging.error(r.json())
        return

    clicker = r.json().get('clickerUser')
    user_ID = clicker.get('id')
    totalCoins = int(clicker.get('totalCoins'))
    balanceCoins = int(clicker.get('balanceCoins'))
    update_date = datetime.datetime.fromtimestamp(clicker.get('lastSyncUpdate')).strftime('%Y-%m-%d %H:%M:%S')
    result = f"💰  Баланс: {balanceCoins:,} \n" \
             f"⭐️  Всего: {totalCoins:,} \n" \
             f"🆔  ID пользователя: {user_ID} \n" \
             f"🔄  Обновление: {update_date}"
    balance = result.replace(',', ' ')
    logging.info(update_date)
    return balance


def send_to_group():
    balance = get_balance()

    logging.info(balance.replace('\n', '| ') + '\n')
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": GROUP_ID, "text": balance})
    if r.status_code != 200:
        logging.error(r.json())
        return


if __name__ == '__main__':
    while True:
        send_to_group()
        time.sleep(7200)

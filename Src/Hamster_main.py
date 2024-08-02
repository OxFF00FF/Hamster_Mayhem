import base64
import random
import re
import time
import datetime
import logging
from random import randint
import requests

from utils import *
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s{RESET}", level=logging.INFO)


def buy_upgrade(upgradeId: str) -> dict:
    if upgradeId:
        json_data = {'upgradeId': upgradeId, 'timestamp': int(time.time())}
        response = requests.post('https://api.hamsterkombatgame.io/clicker/buy-upgrade', headers=HEADERS, json=json_data)
        if response.status_code != 200:
            logging.error(f"❌  {response.json()}")
            logging.error(f"🚫  Токен не был предоставлен")
            return
        else:
            return response.json()
    else:
        logging.error(f"upgradeId не предоставлен")


def get_daily_combo_cipher() -> dict:
    combo_response = requests.post('https://api21.datavibe.top/api/GetCombo')
    if combo_response.status_code == 200:
        combo = combo_response.json()['combo']
        date = combo_response.json()['date']
        logging.info(f"Комбо: ({date}) | {combo}")
    else:
        logging.error(f"{combo_response.status_code} | {combo_response.json()}")

    cipher_response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=HEADERS)
    if cipher_response.status_code == 200:
        encoded_cipher = cipher_response.json()['dailyCipher']['cipher']
        cipher = base64.b64decode(encoded_cipher[:3] + encoded_cipher[3 + 1:]).decode('utf-8')
        logging.info(f"Шифр:  {cipher}")
    else:
        logging.error(f"{cipher_response.status_code} | {cipher_response.json()}")

    result = {'cipher': cipher, 'combo': combo, 'combo_date': date}
    return result


def collect_upgrades_info() -> dict:
    response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    data = get_daily_combo_cipher()

    response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    upgradesForBuy = response.json().get('upgradesForBuy', [])

    total_price = 0
    total_profit = 0
    cards = []
    cards_info = ''
    for card in data['combo']:
        for upgrade in upgradesForBuy:
            if card == upgrade['id']:
                available = upgrade['isAvailable']
                if available:
                    available = f"✅  Карта доступна для улучшения"
                    total_price += upgrade['price']
                    total_profit += upgrade['profitPerHourDelta']
                else:
                    error = buy_upgrade(upgrade['id'])['error_message']
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

    result = {'cards': cards,
              'summary': summary,
              'cipher': data['cipher']}

    logging.info(f"{cards_info}{YELLOW}💰 {total_price:,}{RESET} | {MAGENTA}📈 +{total_profit:,}{RESET}")
    return result


def complete_taps():
    response = requests.post('https://api.hamsterkombatgame.io/clicker/sync', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    clickerUser = response.json().get('clickerUser')
    availableTaps = int(clickerUser.get('availableTaps'))
    maxTaps = int(clickerUser.get('maxTaps'))
    earnPerTap = clickerUser.get('earnPerTap')
    tapsRecoverPerSec = clickerUser.get('tapsRecoverPerSec')

    total_remain_time = (maxTaps / tapsRecoverPerSec) / 60
    current_remain_time = (availableTaps / tapsRecoverPerSec) / 60
    if availableTaps == maxTaps:
        count = maxTaps / earnPerTap
        availableTaps = maxTaps - (count * earnPerTap)
        json_data = {'count': int(count), 'availableTaps': availableTaps, 'timestamp': int(time.time())}
        requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=HEADERS, json=json_data)
        logging.info(f"✅  Тапы выполнены")
    else:
        remain = total_remain_time - current_remain_time
        logging.info(f"🚫  Тапы еще не накопились. Следующие тапы через: {remain:.0f} минут")

    response = requests.post('https://api.hamsterkombatgame.io/clicker/boosts-for-buy', headers=HEADERS)
    boostsForBuy = response.json().get('boostsForBuy')
    for boost in boostsForBuy:
        if boost['id'] == 'BoostFullAvailableTaps':
            remain = boost['cooldownSeconds'] / 60
            if remain == 0:
                json_data = {'boostId': boost['id'], 'timestamp': int(time.time())}
                requests.post('https://api.hamsterkombatgame.io/clicker/buy-boost', headers=HEADERS, json=json_data)
                logging.info(f"✅  Использован буст")

                json_data = {'count': int(count), 'availableTaps': availableTaps, 'timestamp': int(time.time())}
                requests.post('https://api.hamsterkombatgame.io/clicker/tap', headers=HEADERS, json=json_data)
                logging.info(f"✅  Тапы выполнены")
            else:
                logging.error(f"🚫  Буст еще не готов. Следующий буст через {remain:.0f} минут. {boost['maxLevel'] + 1 - boost['level']}/{boost['maxLevel']} доступно")


def complete_daily_tasks():
    response = requests.post('https://api.hamsterkombatgame.io/clicker/list-tasks', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    task_list = response.json().get('tasks', [])
    any_completed = False
    for task in task_list:
        if not task['isCompleted']:
            json_data = {'taskId': task['id']}
            requests.post('https://api.hamsterkombatgame.io/clicker/check-task', headers=HEADERS, json=json_data)
            logging.info(f"⭐️  Задание `{task['id']}` выполнено")
            any_completed = True
    if any_completed:
        logging.info("✅  Все задания выполнены")
    else:
        logging.info("ℹ️  Задания на сегодня уже выполнены")


def complete_daily_chipher():
    response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    isClaimed = response.json()['dailyCipher']['isClaimed']
    if not isClaimed:
        cipher = get_daily_combo_cipher()['cipher'].upper()
        json_data = {'cipher': cipher}
        response = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-cipher', headers=HEADERS, json=json_data)
        remain = response.json().get('dailyCipher').get('remainSeconds') / 60
        logging.info(f"⚡️  Ежедневный шифр получен ({cipher}). Следующий шифр будет доступен через: {remain:.0f} часов")
    else:
        logging.info(f"ℹ️  Шифр сегодня уже получен")


def complete_daily_combo(buy_anyway=False):
    response = requests.post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    isClaimed = response.json()['dailyCombo']['isClaimed']
    if not isClaimed:
        upgrades_info = collect_upgrades_info()
        cards = upgrades_info['cards']

        if buy_anyway:
            for card in cards:
                if card['available']:
                    upgradeId = card['id']
                    buy_upgrade(upgradeId)
                    logging.info(f"✅  Куплена карта `{upgradeId}`")
                logging.info(f"🚫  Ежедневное комбо не выполнено. Были куплены только доступные карты")

        if all(card['available'] for card in cards):
            for card in cards:
                upgradeId = card['id']
                buy_upgrade(upgradeId)
                logging.info(f"✅  Куплена карта `{upgradeId}`")
            requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-combo', headers=HEADERS)
            logging.info(f"✅  Ежедневное комбо выполнено")
    else:
        logging.info(f"ℹ️  Комбо сегодня уже получено")


def complete_daily_minigame():
    response = requests.post('https://api.hamsterkombatgame.io/clicker/config', headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"❌  {response.json()}")
        logging.error(f"🚫  Токен не был предоставлен")
        return

    isClaimed = response.json().get('dailyKeysMiniGame').get('isClaimed')
    if not isClaimed:
        levelConfig = response.json().get('dailyKeysMiniGame').get('levelConfig')
        logging.info(f"| {datetime.datetime.today().date()} | {levelConfig} |")

        start_game = requests.post('https://api.hamsterkombatgame.io/clicker/start-keys-minigame', headers=HEADERS)
        if start_game.status_code == 200:
            match = re.search(pattern=r'Bearer (.*?)(\d+$)', string=HAMSTER_TOKEN)
            if match:
                user_id = match.group(2)
                unix_time_from_start_game = f"0{randint(12, 26)}{random.randint(10000000000, 99999999999)}"[:10]
                cipher = base64.b64encode(f"{unix_time_from_start_game}|{user_id}".encode("utf-8")).decode("utf-8")

            json_data = {'cipher': cipher}
            end_game_response = requests.post('https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame', headers=HEADERS, json=json_data)
            if end_game_response.status_code == 200:
                logging.info(f"✅  Миниигра пройдена. Получено ключей: 1")
            else:
                logging.error(f"{end_game_response.status_code} | {end_game_response.json()}")
        else:
            match = re.search(pattern=r'Please wait (.*?) before next attempt', string=response.json().get('error_message'))
            remain = int(match.group(1).split('.')[0]) / 60
            logging.error(f"🚫  Миниигра недоступна. Следующая попытка через: {remain:.0f} минут")
    else:
        logging.info(f"ℹ️  Миниигра сегодня уже пройдена")


def daily_info():
    upgrades_info = collect_upgrades_info()
    cipher = upgrades_info['cipher']
    morse = text_to_morse(cipher)
    combo = '\n'.join(card['description'] for card in upgrades_info['cards'])

    result = {'date': f"📆  {datetime.datetime.today().date()}",
              'cipher': f"📇  Шифр:  {cipher} | {morse} |",
              'summary': f"{upgrades_info['summary']}",
              'combo': combo}

    text = f"{result['date']} \n\n"
    text += f"{result['combo']} \n"
    text += f"{result['cipher']} \n\n"
    text += f"{result['summary']}"
    if '🚫' in result['combo']:
        text += "⚠️Сегодня вам не все карты доступны"
    logging.info(f"\n{text}")
    return result


if __name__ == '__main__':
    daily_info()
    # complete_taps()
    # complete_daily_tasks()
    # complete_daily_chipher()
    # complete_keys_chipher()
    # complete_daily_combo()
    pass

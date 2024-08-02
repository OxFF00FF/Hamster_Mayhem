import subprocess
import sys
import logging
import os
import random
import time
import uuid
import threading

try:
    import requests
    from dotenv import load_dotenv
    from spinners import Spinners

except ImportError:
    required_packages = ['requests', 'python-dotenv', 'spinners']
    for package in required_packages:
        try:
            __import__('requests')
        except ImportError:
            print(f"{package} не найден. Устанавливаю...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            import requests
            from dotenv import load_dotenv
            from spinners import Spinners

# --- CONFIG --- #

load_dotenv()
logging.basicConfig(level=logging.INFO, format=' | %(asctime)s - %(levelname)s |\x1b[36m %(message)s \x1b[0m')

loading_active = True

APP_TOKEN = os.getenv('APP_TOKEN')
PROMO_ID = os.getenv('PROMO_ID')
EVENTS_DELAY = 20000

SEND_TO_GROUP = True
BOT_TOKEN = os.getenv('BOT_TOKEN')
HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
GROUP_URL = os.getenv('GROUP_URL')
HAMSTER_HEADERS = {
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

# --- CONFIG --- #


def loading(default=True, spinner_name=None, spinner_list=None):
    if spinner_list:
        spinners = [spinner_name.name for spinner_name in Spinners]
        text = ''
        for spinner in spinners:
            text += f"{spinner}\n"
        return text

    if spinner_name is not None:
        spinners = [spinner_name.name for spinner_name in Spinners]
        for spinner_item in spinners:
            if spinner_item == spinner_name:
                spinner = Spinners[spinner_name]
                while loading_active:
                    for frame in spinner.value['frames']:
                        print(f"\r\033[34m {frame} \x1b[0m", end='', flush=True)
                        time.sleep(0.001 * spinner.value['interval'])
        print(f'Spinner `{spinner_name}` not found')
        return

    if default:
        spinner = ["▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱", "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰", "▱▰▰▰▰▰▰", "▱▱▰▰▰▰▰", "▱▱▱▰▰▰▰", "▱▱▱▱▰▰▰", "▱▱▱▱▱▰▰", "▱▱▱▱▱▱▰"]
        while loading_active:
            for frame in spinner:
                print(f"\r\033[33m {frame} \x1b[0m", end='', flush=True)
                time.sleep(0.3)


def generate_client_id() -> str:
    timestamp = int(time.time() * 1000)
    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
    time.sleep(1)
    return f"{timestamp}-{random_numbers}"


def get_client_token(client_id) -> str:
    HEADERS = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io'}
    json_data = {'appToken': APP_TOKEN, 'clientId': client_id, 'clientOrigin': 'deviceid'}

    response = requests.post('https://api.gamepromo.io/promo/login-client', headers=HEADERS, json=json_data)
    response.raise_for_status()
    time.sleep(2)
    return response.json()['clientToken']


def emulate_progress(token) -> str:
    HEARERS = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
    json_data = {'promoId': PROMO_ID, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}

    response = requests.post('https://api.gamepromo.io/promo/register-event', headers=HEARERS, json=json_data)
    response.raise_for_status()
    time.sleep(1)
    return response.json().get('hasCode', False)


def generate_key(token) -> str:
    HEARERS = {'content-type': 'application/json; charset=utf-8', 'Host': 'api.gamepromo.io', 'Authorization': f'Bearer {token}'}
    json_data = {'promoId': PROMO_ID}

    response = requests.post('https://api.gamepromo.io/promo/create-code', headers=HEARERS, json=json_data)
    response.raise_for_status()
    time.sleep(1)
    return response.json().get('promoCode', '')


def key_generation(apply_promo=False, send_to_group=False) -> str:
    global loading_active

    client_id = generate_client_id()
    logging.info(f'Generated clientId: `{client_id}`')

    CLIENT_TOKEN = get_client_token(client_id)
    logging.info(f'Login successful. Token: `{CLIENT_TOKEN}`')

    has_code = False
    time.sleep(2)
    logging.info(f'Emulate progress...')
    logging.info(f'Проходим велосипеды, чтобы вам не пришлось))')
    progress = 20
    for e, item in enumerate(range(7)):
        delay = EVENTS_DELAY * (random.random() / 3 + 1)
        time.sleep(delay / 1000.0)

        has_code = emulate_progress(CLIENT_TOKEN)
        logging.info(f"[{e + 1}] Status: {progress}%")
        progress += 20
        if has_code:
            break

    promoCode = generate_key(CLIENT_TOKEN)
    logging.info(f'Generated key: \033[32m`{promoCode}`\x1b[0m')

    if apply_promo:
        response = requests.post('https://api.hamsterkombatgame.io/clicker/get-promos', headers=HAMSTER_HEADERS)
        if response.status_code != 200:
            logging.error(f"❌  {response.json()}")
            logging.error(f"🚫  Токен не был предоставлен")
            return

        states = response.json()['states']
        for state in states:
            if state['promoId'] == PROMO_ID:
                keys_today = state['receiveKeysToday']
                remain = state['receiveKeysRefreshSec'] / 3600

        promos = response.json()['promos']
        for promo in promos:
            if promo['promoId'] == PROMO_ID:
                keys_limit = promo['keysPerDay']
                promo_title = promo['title']['en']

        logging.info(f"Получено ключей сегодня: {keys_today}/{keys_limit}")
        if keys_today == keys_limit:
            logging.info(f"ℹ️  Все ключи в игре `{promo_title}` сегодня уже получены. Следующие ключи будут доступны через: {remain:.0f} часов")

        else:
            logging.info("Activation promo code...")
            json_data = {'promoCode': promoCode}
            apply_promo = requests.post('https://api.hamsterkombatgame.io/clicker/apply-promo', headers=HAMSTER_HEADERS, json=json_data)
            if apply_promo.status_code == 200:
                logging.info(f"✅  Промокод `{promoCode}` успешно активирован. Доступно ключей сегодня: {keys_today + 1}/{keys_limit}\n")
            else:
                logging.error(f"{apply_promo.status_code} | {apply_promo.json()}")

    if send_to_group:
        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": {GROUP_ID}, "text": promoCode})
        if response.status_code != 200:
            print(response.json())
            return
        else:
            logging.info(f"Ключ был отправлен в группу `{GROUP_URL}`")

    return promoCode


def start(keys_count=None, apply_promo=False, send_to_group=False):
    global loading_active

    if keys_count is None or keys_count == "":
        logging.info("Keys count is not provided. Generating 1 key by default\n")
        keys_count = 1
    else:
        logging.info(f"Generating {keys_count} keys\n")

    time.sleep(2)
    keys_count = int(keys_count)
    file_path = os.path.abspath('generated_keys.txt')

    with open(file_path, 'w') as empty_file:
        pass

    with open(file_path, 'a') as file:
        for e, _ in enumerate(range(keys_count)):
            logging.info(f"Generating [{e+1}/{keys_count}] key")

            key = key_generation(apply_promo=apply_promo, send_to_group=send_to_group)
            file.write(f'{key}\n')
            logging.info(f"Ключ `{key}` сохранён в файл `{file_path}`\n")

    logging.info(f"Все ключи сохранены в файл `{file_path}`")


if __name__ == '__main__':
    if HAMSTER_TOKEN == 'Place_Hamster_Token_Here':
        logging.warning(f"HAMSTER_TOKEN не предоставлен. Ключи не будут добавлены в ваш аккаут!")

    try:
        KEYS_COUNT = input("Введите количество ключей для генерации (оставьте пустым для значения по умолчанию): ")

        apply = input("Активаровать ключи после получения? Y(да)/N(нет): ")
        if str(apply.lower()) == 'y'.lower():
            APPLY_PROMO = True
        elif str(apply.lower()) == 'n'.lower():
            APPLY_PROMO = False
        else:
            logging.error(f'Такой опции нет!')
            exit()

        main_thread = threading.Thread(target=start, args=(KEYS_COUNT, APPLY_PROMO, SEND_TO_GROUP))
        loading_thread = threading.Thread(target=loading, daemon=True)

        loading_thread.start()
        main_thread.start()

        main_thread.join()

    except Exception as E:
        logging.error(f'Error: {E}')

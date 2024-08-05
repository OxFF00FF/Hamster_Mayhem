import logging
import os
import threading

from Src.utils import WHITE, RESET, YELLOW, banner, loading
from Src.Hamster import HamsterKombatClicker

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)

# --- CONFIG --- #

send_to_group = True
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')


# --- CONFIG --- #


def show_menu():
    memu = f"""
    Главное меню
    1. Выполнить клики
    2. Завершить задания
    3. Получить шифр
    4. Выполнить комбо
    5. Пройти миниигру
    6. Получить промокоды
    7. Использовать промокод
    """

    print(memu.strip())
    choice = input("\nВыберите действие (1/2/3/4/5/6/7): ")
    print("~" * 60)
    return choice


def generate_promocodes():
    logging.basicConfig(format=f" | {WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)

    hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)

    keys_count_to_generate = input(f"Введите количество ключей для генерации (enter значение по умолчанию): ")
    if keys_count_to_generate == '':
        keys_count_to_generate = 1
        logging.info("Количество ключей не предоставлено. Генерируется 1 ключ по умолчанию")
        exit(1)

    if int(keys_count_to_generate) <= 0:
        logging.error(f"Количество должно быть числом больше 0")
        exit(1)

    main_thread = threading.Thread(target=hamster_client.get_promocodes, args=(keys_count_to_generate, send_to_group, BOT_TOKEN, GROUP_ID))
    loading_thread = threading.Thread(target=loading)

    loading_thread.start()
    main_thread.start()

    main_thread.join()


if __name__ == '__main__':
    # print(banner)
    show_menu()

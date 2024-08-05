import logging
import os
import threading

from Src.utils import WHITE, RESET, banner, loading, loading_event, line_after, line_before, YELLOW, CYAN
from Src.Hamster import HamsterKombatClicker

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)

# --- CONFIG --- #

send_to_group = True
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')

hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)

# --- CONFIG --- #


def show_menu():
    memu = f"""
    Главное меню
    👆  {YELLOW}1.{RESET} Выполнить клики
    🌟  {YELLOW}2.{RESET} Завершить задания
    🗃   {YELLOW}3.{RESET} Получить шифр
    💰  {YELLOW}4.{RESET} Выполнить комбо
    🔑  {YELLOW}5.{RESET} Пройти миниигру
    🎉  {YELLOW}6.{RESET} Получить промокоды
    ℹ️  {YELLOW}7.{RESET} Информация
    🚪  {YELLOW}8.{RESET} Выйти
    """

    print(memu.strip())
    choice = input(f"\n{CYAN}Выберите действие (1/2/3/4/5/6/7/8):{RESET} ")
    line_before()
    return choice


def generate_promocodes():
    keys_count_to_generate = input(f"Введите количество ключей для генерации (enter значение по умолчанию): ")
    if keys_count_to_generate == '':
        keys_count_to_generate = 1
        logging.info("Количество ключей не предоставлено. Генерируется 1 ключ по умолчанию")

    if int(keys_count_to_generate) <= 0:
        logging.error(f"Количество должно быть числом больше 0")
        exit(1)

    main_thread = threading.Thread(target=hamster_client.get_promocodes, args=(keys_count_to_generate, send_to_group, BOT_TOKEN, GROUP_ID))
    loading_thread = threading.Thread(target=loading)

    loading_thread.start()
    main_thread.start()

    main_thread.join()

    loading_event.set()
    loading_thread.join()


def main():
    banner()
    while True:
        choice = show_menu()

        if choice == '1':
            hamster_client.complete_taps()
            line_after()

        elif choice == '2':
            hamster_client.complete_daily_tasks()
            line_after()

        elif choice == '3':
            hamster_client.complete_daily_chipher()
            line_after()

        elif choice == '4':
            hamster_client.complete_daily_combo()
            line_after()

        elif choice == '5':
            hamster_client.complete_daily_minigame()
            line_after()

        elif choice == '6':
            generate_promocodes()
            line_after()

        elif choice == '7':
            hamster_client.daily_info()
            line_after()

        elif choice == '8':
            exit(1)


if __name__ == '__main__':
    main()

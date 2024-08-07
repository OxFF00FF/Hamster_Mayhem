import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from Src.Hamster import HamsterKombatClicker
from Src.utils import WHITE, RESET, YELLOW, CYAN, LIGHT_YELLOW, GREEN, RED, \
    banner, loading, loading_event, line_after, line_before

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)
logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s{WHITE}", level=logging.INFO)

# --- CONFIG --- #

send_to_group = True
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
HAMSTER_TOKEN = os.getenv('HAMSTER_TOKEN')

hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)


# --- CONFIG --- #


def get_status(status):
    return f"{GREEN}ДА{RESET}" if status else f"{RED}НЕТ{RESET}"


def show_menu():
    memu = f"""
    Главное меню
    ⚙️  Отправлять в группу: {get_status(send_to_group)}
     
    ❕   {LIGHT_YELLOW}#.{RESET} {YELLOW}Информация{WHITE}
    👆  {LIGHT_YELLOW}1.{RESET} {YELLOW}Выполнить клики{WHITE}
    🌟  {LIGHT_YELLOW}2.{RESET} {YELLOW}Завершить задания{WHITE}
    🗃  {LIGHT_YELLOW}3.{RESET} {YELLOW}Получить шифр{WHITE}
    💰  {LIGHT_YELLOW}4.{RESET} {YELLOW}Выполнить комбо{WHITE}
    🔑  {LIGHT_YELLOW}5.{RESET} {YELLOW}Пройти миниигру{WHITE}
    🚴  {LIGHT_YELLOW}6.{RESET} {YELLOW}Получить промокоды для Bike Ride 3D{WHITE}
    🎲  {LIGHT_YELLOW}7.{RESET} {YELLOW}Получить промокоды для Chain Cube 2048{WHITE}
    🕹  {LIGHT_YELLOW}8.{RESET} {YELLOW}Получить промокоды для My Clone Army{WHITE}
    🚂  {LIGHT_YELLOW}9.{RESET} {YELLOW}Получить промокоды для Train Miner{WHITE}
    🎉  {LIGHT_YELLOW}*.{RESET} {YELLOW}Пройти сразу все игры{WHITE}
    🔙  {LIGHT_YELLOW}0.{RESET} {YELLOW}Выйти{WHITE}
    """

    print(memu.strip())
    choice = input(f"\n{CYAN}Выберите действие (#/1/2/3/4/5/6/7/8/9/0/*):{RESET} ")
    line_before()
    return choice


def generate_promocodes(apply_promo=False, prefix=None):
    if prefix:
        count = input(f"Введите количество ключей для генерации (enter значение по умолчанию): ")
        if count == '':
            count = 1
            print("Количество ключей не предоставлено. Генерируется 1 ключ по умолчанию")

        if int(count) <= 0:
            logging.error(f"Количество должно быть числом больше 0")
            exit(1)

        main_thread = threading.Thread(target=hamster_client.get_promocodes, args=(count, send_to_group, BOT_TOKEN, GROUP_ID, apply_promo, prefix))
        loading_thread = threading.Thread(target=loading)

        loading_thread.start()
        main_thread.start()

        main_thread.join()

        loading_event.set()
        loading_thread.join()

    else:
        logging.error(f"Префикс игры не узказан")
        exit(1)


def main():
    banner()
    while True:
        choice = show_menu()

        if choice == '#':
            info = hamster_client.daily_info()
            print(info)
            line_after()

        elif choice == '1':
            hamster_client.complete_taps()
            line_after()

        elif choice == '2':
            hamster_client.complete_daily_tasks()
            line_after()

        elif choice == '3':
            hamster_client.complete_daily_chipher()
            line_after()

        elif choice == '4':
            upgrades_info = hamster_client._collect_upgrades_info()
            if all(card['available'] for card in upgrades_info['cards']):
                hamster_client.complete_daily_combo()
            else:
                choice = input(f"Сегодня не все карты доступны! Хотите купить только доступные? Y(да)/N(нет): ")
                if str(choice.lower()) == 'y'.lower():
                    hamster_client.complete_daily_combo(buy_anyway=True)
                elif str(choice.lower()) == 'n'.lower():
                    line_after()
                else:
                    logging.error(f'Такой опции нет!')
            line_after()

        elif choice == '5':
            hamster_client.complete_daily_minigame()
            line_after()

        elif choice == '6':
            choice = input(f"Применить промокоды после получения? Y(да)/N(нет): ")
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='BIKE', apply_promo=True)
            elif str(choice.lower()) == 'n'.lower():
                generate_promocodes(prefix='BIKE')
            else:
                logging.error(f'Такой опции нет!')
            line_after()

        elif choice == '7':
            choice = input(f"Применить промокоды после получения? Y(да)/N(нет): ")
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='CUBE', apply_promo=True)
            elif str(choice.lower()) == 'n'.lower():
                generate_promocodes(prefix='CUBE')
            else:
                logging.error(f'Такой опции нет!')
            line_after()

        elif choice == '8':
            choice = input(f"Применить промокоды после получения? Y(да)/N(нет): ")
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='CLONE', apply_promo=True)
            elif str(choice.lower()) == 'n'.lower():
                generate_promocodes(prefix='CLONE')
            else:
                logging.error(f'Такой опции нет!')
            line_after()

        elif choice == '9':
            choice = input(f"Применить промокоды после получения? Y(да)/N(нет): ")
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='TRAIN', apply_promo=True)
            elif str(choice.lower()) == 'n'.lower():
                generate_promocodes(prefix='TRAIN')
            else:
                logging.error(f'Такой опции нет!')
            line_after()

        elif choice == '*':
            with open('Src/playground_games_data.json', 'r', encoding='utf-8') as f:
                apps = json.loads(f.read())['apps']

            count = input(f"Количество ключей для всех игр (enter значение по умолчанию): ")
            if count == '':
                count = 1
                print("Количество ключей не предоставлено. Генерируется 1 ключ по умолчанию")

            if int(count) <= 0:
                logging.error(f"Количество должно быть числом больше 0")
                exit(1)

            def generate_for_all_games(promo):
                prefix = promo['prefix']
                hamster_client.get_promocodes(count=count, prefix=prefix, send_to_group=send_to_group, bot_token=BOT_TOKEN, group_id=GROUP_ID)

            with ThreadPoolExecutor() as executor:
                executor.map(generate_for_all_games, apps)

            line_after()


def test():
    pass


if __name__ == '__main__':
    main()

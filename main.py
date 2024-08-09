import json
import logging
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from Src.Hamster import HamsterKombatClicker
from Src.utils import WHITE, RESET, YELLOW, CYAN, LIGHT_YELLOW, GREEN, RED, \
    banner, loading, loading_event, line_after, line_before, LIGHT_BLUE, LIGHT_MAGENTA, LIGHT_CYAN

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)


def choose_account(default=True):
    if default:
        print(f'Вы вошли используя `HAMSTER_TOKEN_1` по умолчанию')
        return os.getenv('HAMSTER_TOKEN_1')

    accounts = []
    env_vars = {key: os.getenv(key) for key in os.environ if key in os.environ}
    for key, value in env_vars.items():
        if key.startswith('HAMSTER'):
            accounts.append(value)

    if len(accounts) > 1:
        print(f"Обнаружено аккаунтов {len(accounts)}: ")
        for e, token in enumerate(accounts):
            hamster = HamsterKombatClicker(token)
            account_info = hamster.get_account_info()
            username = account_info['username']
            first_name = account_info['firstName']
            last_name = account_info['lastName']
            print(f"[{e + 1}] · {first_name} {last_name} ({username})")

        account_choice = input(f"\nКакой аккаунт хотите использовать?\nВыберите номер: ")
        if account_choice == '1':
            return accounts[0]

        elif account_choice == '2':
            return accounts[1]

    else:
        return accounts[0]


# --- CONFIG --- #

send_to_group = True
HAMSTER_TOKEN = choose_account(default=True)
hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)

# --- CONFIG --- #


def get_status(status):
    return f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"


def menu():
    activities = hamster_client._activity_cooldowns()
    keys_per_day = 4
    for activity in activities:
        if 'taps' in activity:
            taps_status = get_status(activity['taps']['isClaimed'])
            taps_cooldown = activity['taps']['remain']
        if 'tasks' in activity:
            task_status = get_status(activity['tasks']['isClaimed'])
            task_cooldown = activity['tasks']['remain']
        if 'cipher' in activity:
            cipher_status = get_status(activity['cipher']['isClaimed'])
            cipher_cooldown = activity['cipher']['remain']
        if 'combo' in activity:
            combo_status = get_status(activity['combo']['isClaimed'])
            combo_cooldown = activity['combo']['remain']
        if 'minigame' in activity:
            minigame_status = get_status(activity['minigame']['isClaimed'])
            minigame_cooldown = activity['minigame']['remain']
        if 'promo' in activity:
            bike = cube = clon = trin = ""
            bike_keys = cube_keys = clon_keys = trin_keys = 0
            bike_cooldown = cube_cooldown = clon_cooldown = trin_cooldown = "n/a"
            bike_status = cube_status = clon_status = trin_status = "n/a"

            for promo in activity['promo']:
                if promo['name'] == 'Bike Ride 3D':
                    bike = promo['name']
                    bike_keys = promo['keys']
                    bike_cooldown = promo['remain']
                    bike_status = get_status(promo['isClaimed'])
                else:
                    bike = 'Bike Ride 3D'

                if promo['name'] == 'Chain Cube 2048':
                    cube = promo['name']
                    cube_keys = promo['keys']
                    cube_cooldown = promo['remain']
                    cube_status = get_status(promo['isClaimed'])
                else:
                    cube = 'Chain Cube 2048'

                if promo['name'] == 'My Clone Army':
                    clon = promo['name']
                    clon_keys = promo['keys']
                    clon_cooldown = promo['remain']
                    clon_status = get_status(promo['isClaimed'])
                else:
                    clon = 'My Clone Army'

                if promo['name'] == 'Train Miner':
                    trin = promo['name']
                    trin_keys = promo['keys']
                    trin_cooldown = promo['remain']
                    trin_status = get_status(promo['isClaimed'])
                else:
                    trin = 'Train Miner'

    max_width = max(len(bike), len(cube), len(clon), len(trin))
    memu = (
        f"Настройки \n"
        f"  ⚙️  Отправлять промокоды в группу: {get_status(send_to_group)}\n\n"
        f"Главное меню \n"
        f"  Какую активность хотите выполнить? \n"
        f"  {LIGHT_YELLOW}# |  {RESET}📝 {YELLOW}Информация {WHITE} \n"
        f"  {LIGHT_YELLOW}1 |  {RESET}👆 {YELLOW}Клики {WHITE:<15}                           {taps_status} · Осталось: {taps_cooldown}\n"
        f"  {LIGHT_YELLOW}2 |  {RESET}📑 {YELLOW}Задания {WHITE:<15}                         {task_status} · Осталось: {task_cooldown} \n"
        f"  {LIGHT_YELLOW}3 |  {RESET}🗃 {YELLOW}Шифр {WHITE:<15}                            {cipher_status} · Осталось: {cipher_cooldown} \n"
        f"  {LIGHT_YELLOW}4 |  {RESET}💰 {YELLOW}Комбо {WHITE:<15}                           {combo_status} · Осталось: {combo_cooldown} \n"
        f"  {LIGHT_YELLOW}5 |  {RESET}🔑 {YELLOW}Миниигра {WHITE:<15}                        {minigame_status} · Осталось: {minigame_cooldown} \n"
        f"  {LIGHT_YELLOW}6 |  {RESET}🚴 {YELLOW}Промокоды {LIGHT_YELLOW}{bike:<{max_width}} {WHITE}  {bike_keys}/{keys_per_day}  {bike_status} · Осталось: {bike_cooldown} \n"
        f"  {LIGHT_YELLOW}7 |  {RESET}🎲 {YELLOW}Промокоды {LIGHT_BLUE}{cube:<{max_width}} {WHITE}  {cube_keys}/{keys_per_day}  {cube_status} · Осталось: {cube_cooldown} \n"
        f"  {LIGHT_YELLOW}8 |  {RESET}🕹 {YELLOW}Промокоды {LIGHT_MAGENTA}{clon:<{max_width}} {WHITE}  {clon_keys}/{keys_per_day}  {clon_status} · Осталось: {clon_cooldown} \n"
        f"  {LIGHT_YELLOW}9 |  {RESET}🚂 {YELLOW}Промокоды {LIGHT_CYAN}{trin:<{max_width}} {WHITE}  {trin_keys}/{keys_per_day}  {trin_status} · Осталось: {trin_cooldown} \n"
        f"  {LIGHT_YELLOW}* |  {RESET}🎉 {YELLOW}Промокоды для всех игр {WHITE} \n"
        f"  {LIGHT_YELLOW}$ |  {RESET}💲 {YELLOW}Список самых выгодных карт {WHITE} \n"
        f"  {LIGHT_YELLOW}+ |  {RESET}⚡️ {YELLOW}Купить карту `+ID_Карты` (напрмиер +dao) {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔙 {YELLOW}Выйти{WHITE}"
    )

    print(memu.strip())


def generate_promocodes(apply_promo=False, prefix=None):
    if prefix:
        count = input(f"Количество ключей для генерации Enter(по умолчанию 1): ")
        if count == '':
            count = 1
            print("\nКоличество ключей не указано. Генерируется 1 ключ по умолчанию")

        if int(count) <= 0:
            logging.error(f"\nКоличество должно быть числом больше 0")
            exit(1)

        main_thread = threading.Thread(target=hamster_client.get_promocodes, args=(count, send_to_group, apply_promo, prefix))
        loading_thread = threading.Thread(target=loading)

        loading_thread.start()
        main_thread.start()

        main_thread.join()

        loading_event.set()
        loading_thread.join()

    else:
        logging.error(f"Префикс игры не узказан")
        exit(1)


def handle_choice(choice):
    if choice == '#':
        print(hamster_client.daily_info())
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
            choice = input(f"Сегодня не все карты доступны!\nХотите купить только доступные? Y(да) / Enter(нет): ")
            if str(choice.lower()) == 'y'.lower():
                hamster_client.complete_daily_combo(buy_anyway=True)
        line_after()

    elif choice == '5':
        hamster_client.complete_daily_minigame()
        line_after()

    elif choice == '6':
        choice = input(f"Хотите применить прмокоды после получения?\nY(да) / Enter(Нет): ")
        if str(choice.lower()) == 'y'.lower():
            generate_promocodes(prefix='BIKE', apply_promo=True)
        else:
            generate_promocodes(prefix='BIKE')
        line_after()

    elif choice == '7':
        choice = input(f"Хотите применить прмокоды после получения?\nY(да) / Enter(Нет): ")
        if str(choice.lower()) == 'y'.lower():
            generate_promocodes(prefix='CUBE', apply_promo=True)
        else:
            generate_promocodes(prefix='CUBE')
        line_after()

    elif choice == '8':
        choice = input(f"Хотите применить прмокоды после получения?\nY(да) / Enter(Нет): ")
        if str(choice.lower()) == 'y'.lower():
            generate_promocodes(prefix='CLONE', apply_promo=True)
        else:
            generate_promocodes(prefix='CLONE')
        line_after()

    elif choice == '9':
        choice = input(f"Хотите применить прмокоды после получения?\nY(да) / Enter(Нет): ")
        if str(choice.lower()) == 'y'.lower():
            generate_promocodes(prefix='TRAIN', apply_promo=True)
        else:
            generate_promocodes(prefix='TRAIN')
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

        choice = input(f"Хотите применить прмокоды после получения?\nY(да) / Enter (Нет): ")
        if str(choice.lower()) == 'y'.lower():
            choice = True
        else:
            choice = False

        def generate_for_all_games(promo):
            prefix = promo['prefix']
            hamster_client.get_promocodes(count=count, prefix=prefix, send_to_group=send_to_group, apply_promo=choice)

        with ThreadPoolExecutor() as executor:
            executor.map(generate_for_all_games, apps)
        line_after()

    elif choice == '$':
        top_10_cards = hamster_client.evaluate_cards()
        print(f"Топ 20 самых выгодных карт (показаны только доступные для покупки): \n")
        for card in top_10_cards:
            print(
                f"🏷  {LIGHT_YELLOW}{card['name']} · `{card['section']}`{WHITE} ID ({card['id']}) \n"
                f"💰  Стоимость: {YELLOW}{card['price']:,}{WHITE} · +{card['profitPerHour']} в час \n"
                f"⌚️  Окупаемость (в часах):{LIGHT_MAGENTA} {card['payback_period']}{WHITE} \n"
                f"📊  Коэффициент рентабельности:{LIGHT_CYAN} {card['profitability_ratio']:.5f}{WHITE}"
            )
            print("-" * 30)
        line_after()

    elif choice.startswith('+'):
        match = re.search(pattern=r'\+(.*?)$', string=choice)
        if match:
            upgrade_id = match.group(1)
            hamster_client._buy_upgrade(upgradeId=upgrade_id)
        line_after()

    elif choice == '0':
        exit(1)

    else:
        print("Такой опции нет")
        line_after()


def main():
    banner()
    hamster_client.login()
    menu()

    while True:
        manu_choice = input(f"\nВыберите действие\n{CYAN}(#/1/2/3/4/5/6/7/8/9/*/$/+/0):{RESET} ")
        line_before()
        handle_choice(manu_choice)


def test():
    pass


if __name__ == '__main__':
    main()

import asyncio
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from Src.Hamster import HamsterKombatClicker
from Src.utils import WHITE, RESET, YELLOW, CYAN, LIGHT_YELLOW, GREEN, RED, LIGHT_BLUE, LIGHT_MAGENTA, LIGHT_CYAN, \
    banner, line_after, line_before

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)


def choose_account(default=True, token_number='HAMSTER_TOKEN_1'):
    if default:
        print(f'Вы вошли используя `{token_number}` по умолчанию')
        return os.getenv('HAMSTER_TOKEN_1')

    accounts = []
    env_vars = {key: os.getenv(key) for key in os.environ if key in os.environ}
    for key, value in env_vars.items():
        if key.startswith('HAMSTER'):
            accounts.append(value)

    if len(accounts) > 1:
        print(f"Обнаружено аккаунтов {len(accounts)}: ")
        account_dict = {}
        for e, token in enumerate(accounts):
            hamster = HamsterKombatClicker(token)
            account_info = hamster.get_account_info()
            username = account_info['username']
            first_name = account_info['firstName']
            last_name = account_info['lastName']
            print(f"[{e + 1}] · {first_name} {last_name} ({username})")
            account_dict[str(e + 1)] = token

        account_choice = input(f"\nКакой аккаунт хотите использовать?\nВыберите номер: ")

        if account_choice in account_dict:
            return account_dict[account_choice]
        else:
            print("Некорректный выбор. Попробуйте снова.")
            return choose_account(default=False)
    else:
        return accounts[0]


# --- CONFIG --- #

send_to_group = False
save_to_file = False
HAMSTER_TOKEN = choose_account()
hamster_client = HamsterKombatClicker(HAMSTER_TOKEN)


# --- CONFIG --- #

def generate_promocodes(prefix='', apply_promo=False):
    count = input(f"Количество промокодов для генерации Enter(по умолчанию 1): ")
    if count == '':
        count = 1
        print("\nКоличество промокодов не указано. Генерируется 1 промокод по умолчанию")

    if int(count) <= 0:
        logging.error(f"\nКоличество должно быть числом больше 0")

    try:
        asyncio.run(hamster_client.get_promocodes(count, send_to_group, apply_promo, prefix))

    except Exception as e:
        logging.error(e)

    finally:
        pass


def get_status(status):
    return f"{GREEN}✅{RESET}" if status else f"{RED}🚫{RESET}"


def main_menu():
    activities = hamster_client._activity_cooldowns()
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

    memu = (
        f"Настройки \n"
        f"  ⚙️  Отправлять в группу:  {get_status(send_to_group)}\n"
        f"  ⚙️  Сохранять в файл:     {get_status(save_to_file)}\n\n"
        f"Главное меню \n"
        f"  Какую активность хотите выполнить? \n"
        f"  {LIGHT_YELLOW}# |  {RESET}📝 {YELLOW}Информация {WHITE} \n"
        f"  {LIGHT_YELLOW}1 |  {RESET}👆 {YELLOW}Клики {WHITE}       {taps_status} · Осталось: {taps_cooldown}\n"
        f"  {LIGHT_YELLOW}2 |  {RESET}📑 {YELLOW}Задания {WHITE}     {task_status} · Осталось: {task_cooldown} \n"
        f"  {LIGHT_YELLOW}3 |  {RESET}🔍 {YELLOW}Шифр {WHITE}        {cipher_status} · Осталось: {cipher_cooldown} \n"
        f"  {LIGHT_YELLOW}4 |  {RESET}🔑 {YELLOW}Миниигра {WHITE}    {minigame_status} · Осталось: {minigame_cooldown} \n"
        f"  {LIGHT_YELLOW}5 |  {RESET}💰 {YELLOW}Комбо {WHITE}       {combo_status} · Осталось: {combo_cooldown} \n"
        f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}Промокоды {WHITE}    \n"
        f"  {LIGHT_YELLOW}$ |  {RESET}💲 {YELLOW}Список самых выгодных карт {WHITE} \n"
        f"  {LIGHT_YELLOW}+ |  {RESET}⭐️ {YELLOW}Купить карту `+ID_Карты` (напрмиер +dao) {WHITE} \n"
        f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}Показать меню {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}Выйти{WHITE}"
    )
    print(memu.strip())


def playground_menu():
    promos = hamster_client._get_promos()[0]['promo']

    keys_per_day = 4
    bike = cube = clon = trin = ""
    bike_keys = cube_keys = clon_keys = trin_keys = 0
    bike_cooldown = cube_cooldown = clon_cooldown = trin_cooldown = "n/a"
    bike_status = cube_status = clon_status = trin_status = "n/a"

    for promo in promos:
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

        if promo['name'] == 'Merge Away':
            mrge = promo['name']
            mrge_keys = promo['keys']
            mrge_cooldown = promo['remain']
            mrge_status = get_status(promo['isClaimed'])
        else:
            mrge = 'Merge Away'

        if promo['name'] == 'Twerk Race':
            twrk = promo['name']
            twrk_keys = promo['keys']
            twrk_cooldown = promo['remain']
            twrk_status = get_status(promo['isClaimed'])
        else:
            twrk = 'Twerk Race'

    max_width = max(len(bike), len(cube), len(clon), len(trin), len(mrge), len(twrk))
    memu = (
        f"\n🎮  Игровая площадка \n"
        f"  Для какой игры хотите получить промокоды? \n"
        f"  {LIGHT_YELLOW}1 |  {RESET}🚴 {YELLOW} {LIGHT_YELLOW}{bike:<{max_width}} {WHITE}  {bike_keys}/{keys_per_day}  {bike_status} · Осталось: {bike_cooldown} \n"
        f"  {LIGHT_YELLOW}2 |  {RESET}🎲 {YELLOW} {LIGHT_BLUE}{cube:<{max_width}} {WHITE}  {cube_keys}/{keys_per_day}  {cube_status} · Осталось: {cube_cooldown} \n"
        f"  {LIGHT_YELLOW}3 |  {RESET}🎮 {YELLOW} {LIGHT_MAGENTA}{clon:<{max_width}} {WHITE}  {clon_keys}/{keys_per_day}  {clon_status} · Осталось: {clon_cooldown} \n"
        f"  {LIGHT_YELLOW}4 |  {RESET}🚂 {YELLOW} {LIGHT_CYAN}{trin:<{max_width}} {WHITE}  {trin_keys}/{keys_per_day}  {trin_status} · Осталось: {trin_cooldown} \n"
        f"  {LIGHT_YELLOW}5 |  {RESET}🙍‍ {YELLOW} {GREEN}{mrge:<{max_width}} {WHITE}  {mrge_keys}/{keys_per_day}  {mrge_status} · Осталось: {mrge_cooldown} \n"
        f"  {LIGHT_YELLOW}6 |  {RESET}🏃 {YELLOW} {CYAN}{twrk:<{max_width}} {WHITE}  {twrk_keys}/{keys_per_day}  {twrk_status} · Осталось: {twrk_cooldown} \n"
        f"  {LIGHT_YELLOW}* |  {RESET}🎉 {YELLOW} Для всех игр {WHITE} \n"
        f"  {LIGHT_YELLOW}9 |  {RESET}🔙 {YELLOW} В главное меню {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} Выйти {WHITE} \n"
    )
    print(memu.strip())


def handle_main_menu_choice(choice):
    if choice == '#':
        line_after()
        print(hamster_client.daily_info())

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
        hamster_client.complete_daily_minigame()
        line_after()

    elif choice == '5':
        upgrades_info = hamster_client._collect_upgrades_info()
        if all(card['available'] for card in upgrades_info['cards']):
            hamster_client.complete_daily_combo()
        else:
            choice = input(f"Сегодня не все карты доступны!\nХотите купить только доступные? Y(да) / Enter(нет): ")
            if str(choice.lower()) == 'y'.lower():
                hamster_client.complete_daily_combo(buy_anyway=True)
        line_after()

    elif choice == '6':
        handle_playground_menu()

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

    elif choice == 'm':
        main_menu()
        line_after()

    elif choice == '0':
        exit(1)

    else:
        print("Такой опции нет")
        line_after()


def handle_playground_menu():
    while True:
        playground_menu()
        choice = input(f"\nВыберите действие\n{CYAN}(1/2/3/4/5/6/*/9/0): {RESET}")
        choice_text = f"\nХотите применить прмокоды после получения?\nY(да) / Enter(Нет): "

        if choice == '1':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='BIKE', apply_promo=True)
            else:
                generate_promocodes(prefix='BIKE')
            line_after()

        elif choice == '2':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='CUBE', apply_promo=True)
            else:
                generate_promocodes(prefix='CUBE')
            line_after()

        elif choice == '3':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='CLONE', apply_promo=True)
            else:
                generate_promocodes(prefix='CLONE')
            line_after()

        elif choice == '4':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='MERGE', apply_promo=True)
            else:
                generate_promocodes(prefix='MERGE')
            line_after()

        elif choice == '5':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='TWERK', apply_promo=True)
            else:
                generate_promocodes(prefix='TWERK')
            line_after()

        elif choice == '6':
            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                generate_promocodes(prefix='TRAIN', apply_promo=True)
            else:
                generate_promocodes(prefix='TRAIN')
            line_after()

        elif choice == '*':
            with open('Src/playground_games_data.json', 'r', encoding='utf-8') as f:
                apps = json.loads(f.read())['apps']

            choice = input(choice_text)
            if str(choice.lower()) == 'y'.lower():
                apply_promo = True
            else:
                apply_promo = False

            count = input(f"\nКоличество промокодов для всех игр Enter(по умолчанию 1): ")
            if count == '':
                count = 1
                print("\nКоличество промокодов не предоставлено. Генерируется 1 по умолчанию")

            if int(count) <= 0:
                logging.error(f"\nКоличество должно быть числом больше 0")
                exit(1)

            def generate_for_all_games(promo):
                prefix = promo['prefix']
                asyncio.run(hamster_client.get_promocodes(count, send_to_group, apply_promo, prefix))

            with ThreadPoolExecutor() as executor:
                executor.map(generate_for_all_games, apps)
            line_after()

        elif choice == '9':
            line_before()
            print('Вы вышли в главное меню')
            line_after()
            return

        elif choice == '0':
            print("Выход")
            line_after()
            exit(1)


def main():
    banner()
    hamster_client.login()
    main_menu()

    while True:
        main_menu_choice = input(f"\nВыберите действие\n{CYAN}(#/1/2/3/4/5/6/$/+/m/0):{RESET} ")
        handle_main_menu_choice(main_menu_choice)
        line_after()


def test():
    pass


if __name__ == '__main__':
    main()

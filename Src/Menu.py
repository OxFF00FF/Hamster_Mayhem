from Src.Colors import *
from Src.Login import hamster_client
from Src.Settings import load_settings, load_setting
from Src.utils import get_status, get_games_data, remain_time

settings = load_settings()


def main_menu():
    activities = hamster_client()._activity_cooldowns()
    taps_status = task_status = cipher_status = combo_status = minigame_status = 'n/a'
    taps_cooldown = task_cooldown = cipher_cooldown = combo_cooldown = minigame_cooldown = 'n/a'

    if activities:
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
    print()
    if load_setting('hamster_token'):
        memu = (
            f"Настройки \n"
            f"  ⚙️  Отправлять в группу:  {get_status(settings['send_to_group'])} (toggle_group · включить/отключить)\n"
            f"  ⚙️  Применять промокоды:  {get_status(settings['apply_promo'])} (toggle_apply · включить/отключить)\n"
            f"  ⚙️  Сохранять в файл:     {get_status(settings['save_to_file'])} (toggle_file  · включить/отключить)\n\n"
            f"Главное меню \n"
            f"  Какую активность хотите выполнить? \n"
            f"  {LIGHT_YELLOW}# |  {RESET}📝 {YELLOW}Информация {WHITE} \n"
            f"  {LIGHT_YELLOW}1 |  {RESET}👆 {YELLOW}Клики {WHITE}       {taps_status} · Осталось: {taps_cooldown}\n"
            f"  {LIGHT_YELLOW}2 |  {RESET}📑 {YELLOW}Задания {WHITE}     {task_status} · Осталось: {task_cooldown} \n"
            f"  {LIGHT_YELLOW}3 |  {RESET}🔍 {YELLOW}Шифр {WHITE}        {cipher_status} · Осталось: {cipher_cooldown} \n"
            f"  {LIGHT_YELLOW}4 |  {RESET}🔑 {YELLOW}Миниигры {WHITE}    {minigame_status} · Осталось: {minigame_cooldown} \n"
            f"  {LIGHT_YELLOW}5 |  {RESET}💰 {YELLOW}Комбо {WHITE}       {combo_status} · Осталось: {combo_cooldown} \n"
            f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}Промокоды {WHITE}    \n"
            f"  {LIGHT_YELLOW}a |  {RESET}🔐 {YELLOW}Аккаунты {WHITE}     \n"
            f"  {LIGHT_YELLOW}$ |  {RESET}💲 {YELLOW}Список самых выгодных карт {WHITE} \n"
            f"  {LIGHT_YELLOW}+ |  {RESET}⭐️ {YELLOW}Купить карту `+ID_Карты` (напрмиер +dao) {WHITE} \n"
            f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}Показать меню {WHITE} \n"
            f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}Выйти{WHITE}"
        )

    else:
        memu = (
            f"Главное меню \n"
            f"  Какую активность хотите выполнить? \n"
            f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}Промокоды {WHITE}    \n"
            f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}Показать меню {WHITE} \n"
            f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}Выйти{WHITE}"
        )
    print(memu.strip())


def playground_menu():
    promos = []
    if settings['hamster_token']:
        promos = hamster_client()._get_promos()

    keys_per_day = 4
    games_data = get_games_data()['apps']
    games_info = {game['title']: {"emoji": game['emoji'], "color": LIGHT_YELLOW} for game in games_data}
    max_width = max(len(game) for game in games_info)

    for promo in promos:
        game_name = promo['name']
        if game_name in games_info:
            games_info[game_name].update({
                "keys": promo['keys'],
                "cooldown": promo['remain'],
                "status": get_status(promo['isClaimed'])
            })

    print()
    menu = "🎮  Игровая площадка \n  Для какой игры хотите получить промокоды? \n"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        keys = game_data.get("keys", 'n/a')
        cooldown = game_data.get("cooldown", "n/a")
        status = game_data.get("status", "n/a")
        emoji = game_data["emoji"]
        color = game_data["color"]

        menu += (f"  {LIGHT_YELLOW}{i} |  {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}  "
                 f"{keys}/{keys_per_day}  {status} · Осталось: {cooldown} \n")

    menu += (
        f"  {LIGHT_YELLOW}* |  {RESET}🎉 {YELLOW} Для всех игр {WHITE} \n"
        f"  {LIGHT_YELLOW}< |  {RESET}🔙 {YELLOW} В главное меню {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} Выйти {WHITE} \n"
    )

    print(menu.strip())


def minigames_menu():
    minigames = []
    if settings['hamster_token']:
        minigames = hamster_client()._get_minigames()

    games_data = get_games_data()['minigames']
    games_info = {game['title']: {"emoji": game['emoji'], "color": LIGHT_YELLOW} for game in games_data}
    max_width = max(len(game) for game in games_info)

    for minigame in minigames:
        game_name = minigame['id']
        if game_name in games_info:
            games_info[game_name].update({
                "cooldown": minigame['remainSeconds'],
                "status": get_status(minigame['isClaimed'])
            })

    print()
    menu = "🎮  Миниигры \n  Какую миниигру хотите пройти? \n"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        cooldown = remain_time(game_data.get("cooldown", "n/a"))
        status = game_data.get("status", "n/a")
        emoji = game_data["emoji"]
        color = game_data["color"]

        menu += f"  {LIGHT_YELLOW}{i} |  {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}  {status} · Осталось: {cooldown} \n"

    menu += (
        f"  {LIGHT_YELLOW}< |  {RESET}🔙 {YELLOW} В главное меню {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} Выйти {WHITE} \n"
    )

    print(menu.strip())

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Login import hamster_client
from Src.utils import get_status, get_games_data, remain_time, localized_text

config = ConfigDB()


def main_menu():
    activities = hamster_client()._activity_cooldowns()

    status_dict = {'taps': ('n/a', 'n/a'), 'tasks': ('n/a', 'n/a'), 'cipher': ('n/a', 'n/a'), 'combo': ('n/a', 'n/a')}

    if activities:
        for activity in activities:
            for key in status_dict.keys():
                if key in activity:
                    status_dict[key] = (get_status(activity[key]['isClaimed']), activity[key]['remain'])

    def activity_line(index, emoji, label, status, cooldown):
        return f"  {LIGHT_YELLOW}{index} |  {RESET}{emoji} {YELLOW}{label} {WHITE}  {status} · {localized_text('left')}: {cooldown} \n"

    menu = f"📚  {localized_text('main_menu_header')}"
    menu += f"  {LIGHT_YELLOW}# |  {RESET}📝 {YELLOW}{localized_text('main_menu_info')} {WHITE} \n"
    menu += activity_line(1, '👆', f"{localized_text('main_menu_taps')}    ", *status_dict['taps'])
    menu += activity_line(2, '📑', f"{localized_text('main_menu_tasks')}   ", *status_dict['tasks'])
    menu += activity_line(3, '🔍', f"{localized_text('main_menu_cipher')}  ", *status_dict['cipher'])
    menu += activity_line(4, '💰', f"{localized_text('main_menu_combo')}   ", *status_dict['combo'])
    menu += (
        f"  {LIGHT_YELLOW}5 |  {RESET}🔑 {YELLOW}{localized_text('main_menu_minigames')} {WHITE} \n"
        f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}{localized_text('main_menu_promocodes')} {WHITE} \n"
        f"  {LIGHT_YELLOW}a |  {RESET}🔐 {YELLOW}{localized_text('main_menu_accounts')} {WHITE} \n"
        f"  {LIGHT_YELLOW}$ |  {RESET}💲 {YELLOW}{localized_text('main_menu_most_profitable_cards')} {WHITE} \n"
        f"  {LIGHT_YELLOW}+ |  {RESET}📥 {YELLOW}{localized_text('main_menu_buy_card')} {WHITE} \n"
        f"  {LIGHT_YELLOW}s |  {RESET}🛠 {YELLOW}{localized_text('main_menu_settings')} {WHITE} \n"
        f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}{localized_text('main_menu_show_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}{localized_text('exit')} {WHITE} \n"
    )
    print(menu)


def main_menu_not_logged():
    menu = localized_text('main_menu_header')
    menu += (
        f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}{localized_text('main_menu_promocodes')} {WHITE} \n"
        f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}{localized_text('main_menu_show_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}{localized_text('exit')} {WHITE} \n"
    )
    print(menu)


def playground_menu():
    promos = []
    if config.hamster_token:
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

    menu = f"🎮  {localized_text('playground_menu_header')}"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        keys = game_data.get("keys", 0)
        cooldown = game_data.get("cooldown", "n/a")
        status = game_data.get("status", f"{RED}❌{WHITE}")
        emoji = game_data["emoji"]
        color = game_data["color"]

        menu += (f"  {LIGHT_YELLOW}{i} |  {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}  "
                 f"{keys}/{keys_per_day}  {status} · {localized_text('left')}: {cooldown} \n")

    menu += (
        f"  {LIGHT_YELLOW}* |  {RESET}🎉 {YELLOW} {localized_text('playground_menu_for_all_games')} {WHITE} \n"
        f"  {LIGHT_YELLOW}< |  {RESET}🔙 {YELLOW} {localized_text('back_to_main_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} {localized_text('exit')} {WHITE} \n"
    )
    print(menu)


def minigames_menu():
    minigames = []
    if config.hamster_token:
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

    menu = f"🎮  {localized_text('minigames_menu_header')}\n"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        cooldown = remain_time(game_data.get("cooldown", "n/a"))
        status = game_data.get("status", "n/a")
        emoji = game_data["emoji"]
        color = game_data["color"]

        menu += f"  {LIGHT_YELLOW}{i} |  {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}  {status} · {localized_text('exit')}: {cooldown} \n"

    menu += (
        f"  {LIGHT_YELLOW}< |  {RESET}🔙 {YELLOW} {localized_text('back_to_main_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} {localized_text('exit')} {WHITE} \n"
    )
    print(menu)


def settings_menu():
    send_to_group = get_status(config.send_to_group)
    apply_promo = get_status(config.apply_promo)
    save_to_file = get_status(config.save_to_file)

    max_length = max(
        len(localized_text('setting_send_to_group')),
        len(localized_text('setting_apply_promo')),
        len(localized_text('setting_save_to_file')),
        len(localized_text('setting_language')),
        len(localized_text('setting_loading_indicator'))
    )

    menu = f"🛠  {localized_text('settings_menu_header')}"
    menu += (
        f"  {LIGHT_YELLOW}1 | {YELLOW} {localized_text('setting_send_to_group').ljust(max_length)} · {send_to_group}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}2 | {YELLOW} {localized_text('setting_apply_promo').ljust(max_length)} · {apply_promo}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}3 | {YELLOW} {localized_text('setting_save_to_file').ljust(max_length)} · {save_to_file}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}4 | {YELLOW} {localized_text('setting_language').ljust(max_length)} · {WHITE}{config.lang} (ru/en) \n"
        f"  {LIGHT_YELLOW}  | {YELLOW} {localized_text('setting_loading_indicator').ljust(max_length)} · {WHITE}{config.spinner} (spinner_<name>/default/list) \n"
    )
    print(menu)

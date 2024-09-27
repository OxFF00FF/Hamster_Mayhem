from Src.Api.Endpoints import HamsterEndpoints
from Src.Colors import *
from Src.utils import get_status, get_games_data, remain_time, localized_text, align_settins, align_main_menu
from Src.HamsterClient import client, config
from config import app_config

not_available = f"{RED}❌{WHITE}"


def main_menu():
    activities = client.get_cooldowns()
    status_dict = {
        'cipher': (not_available, 'n/a'),
        'combo': (not_available, 'n/a'),
        'tasks': (not_available, 'n/a'),
        'taps': (not_available, 'n/a')}

    for key in status_dict.keys():
        if key in activities:
            if activities[key]['remain'] == 0:
                remain = 'n/a'
            status_dict[key] = (get_status(activities[key]['completed']), remain)

    def line(index, emoji, label, status, cooldown):
        return f"  {LIGHT_YELLOW}{index} |  {RESET}{emoji} {YELLOW}{label} {WHITE}  {status} · {localized_text('left')}: {cooldown} \n"

    menu = f"\n📚  {localized_text('main_menu_header')}"
    menu += f"  {LIGHT_YELLOW}# |  {RESET}📝 {YELLOW}{localized_text('main_menu_info')} {WHITE} \n"
    # menu += f"  {LIGHT_YELLOW}@ |  {RESET}🤖 {YELLOW}{localized_text('main_menu_run_bot')} {WHITE} \n"
    # menu += line(1, '👆', f"{align_main_menu(localized_text('main_menu_taps'))}", *status_dict['taps'])
    menu += line(2, '📑', f"{align_main_menu(localized_text('main_menu_tasks'))}", *status_dict['tasks'])
    # menu += line(3, '🔍', f"{align_main_menu(localized_text('main_menu_cipher'))}", *status_dict['cipher'])
    # menu += line(4, '💰', f"{align_main_menu(localized_text('main_menu_combo'))}", *status_dict['combo'])
    menu += (
        f"  {LIGHT_YELLOW}5 |  {RESET}🔑 {YELLOW}{localized_text('main_menu_minigames')} {WHITE} \n"
        f"  {LIGHT_YELLOW}6 |  {RESET}🎁 {YELLOW}{localized_text('main_menu_promocodes')} {WHITE} \n"
        # f"  {LIGHT_YELLOW}a |  {RESET}🔐 {YELLOW}{localized_text('main_menu_accounts')} {WHITE} \n"
        f"  {LIGHT_YELLOW}$ |  {RESET}💲 {YELLOW}{localized_text('main_menu_most_profitable_cards')} {WHITE} \n"
        # f"  {LIGHT_YELLOW}+ |  {RESET}📥 {YELLOW}{localized_text('main_menu_buy_card')} {WHITE} \n"
        f"  {LIGHT_YELLOW}s |  {RESET}🔧 {YELLOW}{localized_text('main_menu_settings')} {WHITE} \n"
        f"  {LIGHT_YELLOW}m |  {RESET}📝 {YELLOW}{localized_text('main_menu_show_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW}{localized_text('exit')} {WHITE}\n"
    )
    if config.has_hamster_token:
        print(menu)
    else:
        main_menu_not_logged()


def main_menu_not_logged():
    menu = localized_text('main_menu_header')
    menu += (
        f"  {LIGHT_YELLOW}6 | {RESET}🎁 {YELLOW}{localized_text('main_menu_promocodes')} {WHITE} \n"
        f"  {LIGHT_YELLOW}s | {RESET}🛠 {YELLOW}{localized_text('main_menu_settings')} {WHITE} \n"
        f"  {LIGHT_YELLOW}m | {RESET}📝 {YELLOW}{localized_text('main_menu_show_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 | {RESET}🔚 {YELLOW}{localized_text('exit')} {WHITE}\n"
    )
    print(menu)


def playground_menu():
    promos = []
    if config.has_hamster_token:
        promos = HamsterEndpoints.get_promos(client.headers)

    games_data = get_games_data()
    games_info = {game['title']: {"emoji": game['emoji']} for game in games_data}
    max_width = max(len(game) for game in games_info)

    for promo in promos:
        game_name = promo.name
        if game_name in games_info:
            games_info[game_name].update({
                "recieved_keys": promo.keys,
                "keys_per_day": promo.per_day,
                "cooldown": promo.remain,
                "status": get_status(promo.is_claimed)
            })

    menu = f"🎮  {localized_text('playground_menu_header')}"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        recieved_keys = game_data.get("recieved_keys", 0)
        keys_per_day = game_data.get("keys_per_day", 0)
        remain = game_data.get("cooldown", "n/a")
        status = game_data.get("status", not_available)
        emoji = game_data["emoji"]

        if recieved_keys >= keys_per_day:
            color = GREEN
        else:
            color = LIGHT_YELLOW

        if not recieved_keys and not keys_per_day:
            keys = 'n/a'
            color = RED
        else:
            keys = f"{recieved_keys}/{keys_per_day}"

        promo_name = f"  {LIGHT_YELLOW}{i:<2} | {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}"
        promo_status = f"{keys}  {status} · {localized_text('left')}: {remain} \n"
        menu += f"{promo_name}  {promo_status}"

    menu += (
        f"  {LIGHT_YELLOW}*  | {RESET}🎉 {YELLOW} {localized_text('playground_menu_for_all_games')} {WHITE} \n"
        f"  {LIGHT_YELLOW}.  | {RESET}🔙 {YELLOW} {localized_text('back_to_main_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0  | {RESET}🔚 {YELLOW} {localized_text('exit')} {WHITE}\n"
    )
    print(menu)


def minigames_menu():
    minigames = []
    if config.has_hamster_token:
        minigames = HamsterEndpoints.get_config(client.headers, 'minigames')

    games_data = get_games_data(apps=False)
    games_info = {game['title']: {"emoji": game['emoji'], "color": LIGHT_YELLOW} for game in games_data}
    max_width = max(len(game) for game in games_info)

    for minigame in minigames:
        game_name = minigame.id
        if game_name in games_info:
            games_info[game_name].update({
                "cooldown": minigame.remainSeconds,
                "status": get_status(minigame.isClaimed)
            })

    menu = f"🎮  {localized_text('minigames_menu_header')}\n"
    for i, (game_name, game_data) in enumerate(games_info.items(), start=1):
        cooldown = remain_time(game_data.get("cooldown", "n/a"))
        status = game_data.get("status", not_available)
        emoji = game_data["emoji"]
        color = game_data["color"]

        menu += f"  {LIGHT_YELLOW}{i} |  {RESET}{emoji} {YELLOW} {color}{game_name:<{max_width}} {WHITE}  {status} · {localized_text('left')}: {cooldown} \n"

    menu += (
        f"  {LIGHT_YELLOW}. |  {RESET}🔙 {YELLOW} {localized_text('back_to_main_menu')} {WHITE} \n"
        f"  {LIGHT_YELLOW}0 |  {RESET}🔚 {YELLOW} {localized_text('exit')} {WHITE}\n"
    )
    print(menu)


def settings_menu():
    send_to_group = get_status(config.send_to_group)
    apply_promo = get_status(config.apply_promo)
    save_to_file = get_status(config.save_to_file)
    chat_id = app_config.CHAT_ID
    group_url = app_config.GROUP_URL

    if config.balance_threshold == 0:
        balance_threshold = get_status(config.balance_threshold)
    else:
        balance_threshold = f"{config.balance_threshold:_}"

    complete_taps = get_status(config.complete_taps)
    complete_tasks = get_status(config.complete_tasks)
    complete_cipher = get_status(config.complete_cipher)
    complete_minigames = get_status(config.complete_minigames)
    complete_combo = get_status(config.complete_combo)
    complete_autobuy_upgrades = get_status(config.complete_autobuy_upgrades)
    complete_promocodes = get_status(config.complete_promocodes)
    all_cards_in_top = get_status(config.all_cards_in_top)

    menu = f"🛠  {localized_text('settings_menu_header')}"
    menu += (
        f"  {LIGHT_YELLOW}  | {YELLOW} {align_settins(localized_text('setting_language'))} · {WHITE}{GREEN}{config.lang.upper()}{WHITE} (ru/en) \n"
        f"  {LIGHT_YELLOW}  | {YELLOW} {align_settins(localized_text('setting_account'))} · {WHITE}{GREEN}{config.account.upper()}{WHITE}\n"
        f"  {LIGHT_YELLOW}g | {YELLOW} {align_settins(localized_text('setting_send_to_group'))} · {send_to_group}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}a | {YELLOW} {align_settins(localized_text('setting_apply_promo'))} · {apply_promo}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}f | {YELLOW} {align_settins(localized_text('setting_save_to_file'))} · {save_to_file}{WHITE} {localized_text('setting_on_off')} {WHITE} \n"
        f"  {LIGHT_YELLOW}t | {YELLOW} {align_settins(localized_text('setting_cards_in_top'))} · {WHITE}{GREEN}{config.cards_in_top}{WHITE} (5/10)\n"
        f"  {LIGHT_YELLOW}s | {YELLOW} {align_settins(localized_text('setting_all_cards_in_top'))} · {WHITE}{GREEN}{all_cards_in_top}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}  | {YELLOW} {align_settins(localized_text('setting_loading_indicator'))} · {WHITE}{GREEN}{config.spinner.upper()}{WHITE} (spinner_<num>/default/list) \n"
    )

    if group_url:
        menu += f"  {LIGHT_YELLOW}  | {YELLOW} {align_settins(localized_text('setting_group_url'))} · {WHITE}{group_url}\n"

    if chat_id:
        menu += f"  {LIGHT_YELLOW}  | {YELLOW} {align_settins(localized_text('setting_chat_id'))} · {WHITE}{chat_id}\n"

    menu += '  ' + '─' * 50 + '\n'
    menu += (
        f"  {LIGHT_YELLOW}1 | {YELLOW} {align_settins(localized_text('setting_balance_threshold'))} · {WHITE}{GREEN}{balance_threshold}{WHITE} (1_<new_value>/1 - disable)\n"
        f"  {LIGHT_YELLOW}2 | {YELLOW} {align_settins(localized_text('setting_complete_taps'))} · {WHITE}{GREEN}{complete_taps}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}3 | {YELLOW} {align_settins(localized_text('setting_complete_tasks'))} · {WHITE}{GREEN}{complete_tasks}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}4 | {YELLOW} {align_settins(localized_text('setting_complete_cipher'))} · {WHITE}{GREEN}{complete_cipher}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}5 | {YELLOW} {align_settins(localized_text('setting_complete_minigames'))} · {WHITE}{GREEN}{complete_minigames}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}6 | {YELLOW} {align_settins(localized_text('setting_complete_combo'))} · {WHITE}{GREEN}{complete_combo}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}7 | {YELLOW} {align_settins(localized_text('setting_complete_autobuy_upgrades'))} · {WHITE}{GREEN}{complete_autobuy_upgrades}{WHITE} {localized_text('setting_on_off')}\n"
        f"  {LIGHT_YELLOW}8 | {YELLOW} {align_settins(localized_text('setting_complete_promocodes'))} · {WHITE}{GREEN}{complete_promocodes}{WHITE} {localized_text('setting_on_off')}\n"
    )
    print(menu)

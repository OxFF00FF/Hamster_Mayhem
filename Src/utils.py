import asyncio
import json
import logging
import os
import time

from spinners import Spinners
from Src.db_SQlite import ConfigDB
from Src.Colors import *

config = ConfigDB()
lang = config.lang


def banner():
    CYN = '\x1b[36m'
    YLW = '\x1b[33m'
    RST = '\x1b[0m'

    print(f"""
    {YLW}     {RST}  {CYN}██╗  ██╗   █████╗   ███╗   ███╗  ███████╗  ████████╗  ███████╗  ██████╗ {RST}  {YLW}     {RST}
    {YLW}    █{RST}  {CYN}██║  ██║  ██╔══██╗  ████╗ ████║  ██╔════╝  ╚══██╔══╝  ██╔════╝  ██╔══██╗{RST}  {YLW}    █{RST}
    {YLW}   ██{RST}  {CYN}███████║  ███████║  ██╔████╔██║  ███████╗     ██║     █████╗    ██████╔╝{RST}  {YLW}   ██{RST}
    {YLW}  ██ {RST}  {CYN}██╔══██║  ██╔══██║  ██║╚██╔╝██║  ╚════██║     ██║     ██╔══╝    ██╔══██╗{RST}  {YLW}  ██ {RST}
    {YLW} ██  {RST}  {CYN}██║  ██║  ██║  ██║  ██║ ╚═╝ ██║  ███████║     ██║     ███████╗  ██║  ██║{RST}  {YLW} ██  {RST}
    {YLW}██   {RST}  {CYN}╚═╝  ╚═╝  ╚═╝  ╚═╝  ╚═╝     ╚═╝  ╚══════╝     ╚═╝     ╚══════╝  ╚═╝  ╚═╝{RST}  {YLW}██   {RST}
    {YLW}█████{RST}  {RST}                      ⚡️  Хомячий Беспредел  ⚡️                       {RST}  {YLW}█████{RST}
    {YLW}   ██{RST}  {RED}    ███╗   ███╗   █████╗   ██╗   ██╗  ██╗  ██╗  ███████╗  ███╗   ███╗   {RST}  {YLW}   ██{RST}
    {YLW}  ██ {RST}  {RED}    ████╗ ████║  ██╔══██╗  ╚██╗ ██╔╝  ██║  ██║  ██╔════╝  ████╗ ████║   {RST}  {YLW}  ██ {RST}
    {YLW} ██  {RST}  {RED}    ██╔████╔██║  ███████║   ╚████╔╝   ███████║  █████╗    ██╔████╔██║   {RST}  {YLW} ██  {RST}
    {YLW}██   {RST}  {RED}    ██║╚██╔╝██║  ██╔══██║    ╚██╔╝    ██╔══██║  ██╔══╝    ██║╚██╔╝██║   {RST}  {YLW}██   {RST}
    {YLW}█    {RST}  {RED}    ██║ ╚═╝ ██║  ██║  ██║     ██║     ██║  ██║  ███████╗  ██║ ╚═╝ ██║   {RST}  {YLW}█    {RST}
    {YLW}     {RST}  {RED}    ╚═╝     ╚═╝  ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝  ╚══════╝  ╚═╝     ╚═╝   {RST}  {YLW}     {RST}
    """)


def text_to_morse(text: str) -> str:
    MORSE_CODE_DICT = {
        'A': '• —', 'B': '— • • •', 'C': '— • — •', 'D': '— • •', 'E': '•', 'F': '• • — •',
        'G': '— — •', 'H': '• • • •', 'I': '• •', 'J': '• — — —', 'K': '— • —', 'L': '• — • •',
        'M': '— —', 'N': '— •', 'O': '— — —', 'P': '• — — •', 'Q': '— — • —', 'R': '• — •',
        'S': '• • •', 'T': '—', 'U': '• • —', 'V': '• • • —', 'W': '• — —', 'X': '— • • —',
        'Y': '— • — —', 'Z': '— — • •', '1': '• — — — —', '2': '• • — — —', '3': '• • • — —',
        '4': '• • • • —', '5': '• • • • •', '6': '— • • • •', '7': '— — • • •', '8': '— — — • •',
        '9': '— — — — •', '0': '— — — — —', ', ': '— — • • — —', '.': '• — • — • —', '?': '• • — — • •',
        "'": '• — — — — •', '!': '— • — • — —', '/': '— • • — •', '(': '— • — — •', ')': '— • — — • —',
        '&': '• — • • •', ':': '— — — • • •', ';': '— • — • — •', '=': '— • • • —', '+': '• — • — •',
        '-': '— • • • • —', '_': '• • — — • —', '"': '• — • • — •', '$': '• • • — • • —', '@': '• — — • — •'}

    text = text.upper()
    morse_text = ' | '.join(MORSE_CODE_DICT.get(char, '') for char in text)
    return morse_text


def countdown_timer(seconds):
    while seconds:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        h = str(h).zfill(2)
        m = str(m).zfill(2)
        s = str(s).zfill(2)
        print(f"\r⏳  Please wait until {h}:{m}:{s} ", flush=True, end="")
        seconds -= 1
        time.sleep(1)
    print(f"\r⏳  Please wait until {h}:{m}:{s} ", flush=True, end="")


def remain_time(seconds):
    try:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        h = str(h).zfill(2)
        m = str(m).zfill(2)
        s = str(s).zfill(2)
        return f"{h}:{m}:{s}"

    except:
        return 'n/a'


async def loading(event):
    spinner = ["▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱", "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰", "▱▰▰▰▰▰▰", "▱▱▰▰▰▰▰", "▱▱▱▰▰▰▰", "▱▱▱▱▰▰▰", "▱▱▱▱▱▰▰", "▱▱▱▱▱▱▰"]
    while not event.is_set():
        for frame in spinner:
            if event.is_set():
                break
            print(f"\r{YELLOW}| {frame} | {WHITE}", end='', flush=True)
            await asyncio.sleep(0.3)


async def loading_v2(event):
    spinner_name = config.spinner
    if spinner_name is not None:
        spinners = [spinner_name.name for spinner_name in Spinners]
        for spinner_item in spinners:
            if spinner_item == spinner_name:
                spinner = Spinners[spinner_name]
                while not event.is_set():
                    for frame in spinner.value['frames']:
                        if event.is_set():
                            break
                        print(f"\r{YELLOW}| {frame.strip()} | {WHITE}", end='', flush=True)
                        await asyncio.sleep(0.3)
        logging.warning(f'Spinner `{spinner_name}` not found')
        await loading(event)

    else:
        await loading(event)


def spinners_list():
    spinners = [spinner_name.name for spinner_name in Spinners]
    text = ''
    for spinner in spinners:
        text += f"{spinner}\n"

    print(text)
    return text


def clear_screen():
    os.system('cls')


def line_before():
    print("\n╭" + "~" * 50 + '╮')


def line_after():
    print('╰' + "~" * 50 + "╯\n")


def get_status(status):
    return f"{GREEN}✅{RESET}" if status else f"{RED}🚫{RESET}"


def generation_status(status):
    return f"{LIGHT_GREEN}{localized_text('received')}{WHITE}" if status else f"{RED}{localized_text('not_recieved')}{WHITE}"


def get_salt(salt):
    try:
        with open('Src/data/salt.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data[salt]

    except Exception as e:
        logging.error(e)


def spinners_table(num_columns=3):
    data = [f"{i + 1}. {spinner_name.name}" for i, spinner_name in enumerate(Spinners)]

    if not data:
        return ""

    num_rows = len(data) // num_columns + (len(data) % num_columns != 0)

    max_widths = [0] * num_columns
    for e, spiner in enumerate(data):
        col_index = e % num_columns
        max_widths[col_index] = max(max_widths[col_index], len(str(spiner)))

    def row_format(row):
        return " | ".join(f"{item:{max_widths[i]}}" for i, item in enumerate(row))

    header = "".join(["_" * (width + 3) for width in max_widths])
    table_ = [header]

    for r in range(num_rows):
        row_ = [data[r * num_columns + i] if r * num_columns + i < len(data) else "" for i in range(num_columns)]
        table_.append(f"| {row_format(row_)} |")

    return "\n".join(table_)


def localized_text(key, *args, **kwargs):
    try:
        with open('Src/data/translations.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode file `translations.json`")
        exit(1)

    # Перевод для указанного языка
    message = translations.get(lang, {}).get(key)

    if message is None:
        # Логирование отсутствующего перевода
        logging.warning(f"No translation available for language code `{lang}` and key `{key}`")

        # Проверка наличия английского перевода
        message = translations.get('en', {}).get(key)
        if message is None:
            logging.warning(f"No English definition found for key `{key}` in translations.json")
            return key

    try:
        return message.format(**kwargs)
    except:
        return message.format(*args)


def align_daily_info(text):
    max_length = max(
        len(localized_text('balance')),
        len(localized_text('total')),
        len(localized_text('keys')),
        len(localized_text('total_purhased_upgraqdes_count')),
        len(localized_text('total_purhased_cards_count'))
    )
    formatted_text = f"{text}: ".replace(',', ' ')
    return formatted_text.ljust(max_length + 2)


def align_summary(text):
    max_length = max(
        len(localized_text('total_profit')),
        len(localized_text('total_price')),
    )
    formatted_text = f"{text}: ".replace(',', ' ')
    return formatted_text.ljust(max_length + 2)


def align_main_menu(text):
    max_length = max(
        len(localized_text('main_menu_taps')),
        len(localized_text('main_menu_tasks')),
        len(localized_text('main_menu_cipher')),
        len(localized_text('main_menu_combo')),
    ) + 3
    return text.ljust(max_length)


def align_settins(text):
    max_length = max(
        len(localized_text('setting_send_to_group')),
        len(localized_text('setting_apply_promo')),
        len(localized_text('setting_save_to_file')),
        len(localized_text('setting_language')),
        len(localized_text('setting_loading_indicator'))
    )
    return text.ljust(max_length)


def get_games_data():
    with open('Src/data/playground_games_data.json', 'r', encoding='utf-8') as f:
        games_data = json.loads(f.read())
    return games_data


def add_new_app(app_token, promo_id, prefix, title, events_count, register_event_timeout, text, emoji):
    games_data = [app for app in get_games_data()['apps'] if app.get('available')]

    new_app = {
        "appToken": app_token,
        "promoId": promo_id,
        "prefix": prefix,
        "title": title,
        "eventsCount": int(events_count),
        "registerEventTimeout": int(register_event_timeout),
        "text": text,
        "emoji": emoji
    }

    games_data.append(new_app)

    with open('Src/data/playground_games_data.json', 'w', encoding='utf-8') as file:
        json.dump(games_data, file, ensure_ascii=False, indent=4)


# add_new_app(app_token='e68b39d2-4880-4a31-b3aa-0393e7df10c7',
#             promo_id='e68b39d2-4880-4a31-b3aa-0393e7df10c7',
#             prefix='TILE ',
#             title='Tile Trio',
#             events_count='22',
#             register_event_timeout='20000',
#             text='🀄️',
#             emoji='🀄️')

async def update_spinner(event, progress_dict, prefix):
    frame_index = 0
    while not event.is_set():
        spinner_frame = get_spinner_frame(config.spinner, frame_index)
        progress_message = progress_dict.get(prefix, "")
        print(f"\r|{spinner_frame}| {WHITE}{progress_message}", end='', flush=True)
        frame_index += 1
        await asyncio.sleep(0.25)


def get_spinner_frame(spinner_name, frame_index):
    if spinner_name == 'hamster':
        frames = create_scrolling_frames('Hamster Kombat. Make your way from the shaved hamster to the grandmaster CEO of the tier-1 crypto exchange. Buy upgrades, complete quests, invite friends and become the best', 20)
        return frames[frame_index % len(frames)]

    try:
        if spinner_name is not None:
            spinners = [spinner_name.name for spinner_name in Spinners]
            for spinner_item in spinners:
                if spinner_item == spinner_name:
                    spinner = Spinners[spinner_name]
                    frames = spinner.value['frames']
                    return frames[frame_index % len(frames)]

    except:
        frames = ["▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱", "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰", "▱▰▰▰▰▰▰", "▱▱▰▰▰▰▰", "▱▱▱▰▰▰▰", "▱▱▱▱▰▰▰", "▱▱▱▱▱▰▰", "▱▱▱▱▱▱▰"]
        return frames[frame_index % len(frames)]


def create_scrolling_frames(text, width):
    frames = []
    padding = ' ' * width
    text = padding + text + padding
    for i in range(len(text) - width + 1):
        frames.append('' + text[i:i + width] + '')
    return frames

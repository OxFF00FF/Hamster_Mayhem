import asyncio
import json
import logging
import os
import time

from spinners import Spinners

from Src.Colors import *


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
        print(f"\rplease wait until {h}:{m}:{s} ", flush=True, end="")
        seconds -= 1
        time.sleep(1)
    print(f"\rplease wait until {h}:{m}:{s} ", flush=True, end="")


def remain_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    h = str(h).zfill(2)
    m = str(m).zfill(2)
    s = str(s).zfill(2)
    return f"{h}:{m}:{s}"


async def loading(event):
    spinner = ["▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱", "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰", "▱▰▰▰▰▰▰", "▱▱▰▰▰▰▰", "▱▱▱▰▰▰▰", "▱▱▱▱▰▰▰", "▱▱▱▱▱▰▰", "▱▱▱▱▱▱▰"]
    while not event.is_set():
        for frame in spinner:
            if event.is_set():
                break
            print(f"\r{YELLOW}| {frame} | {WHITE}", end='', flush=True)
            await asyncio.sleep(0.3)


async def loading_v2(event, spinner_name=None):
    if spinner_name is not None:
        spinners = [spinner_name.name for spinner_name in Spinners]
        for spinner_item in spinners:
            if spinner_item == spinner_name:
                spinner = Spinners[spinner_name]
                while not event.is_set():
                    for frame in spinner.value['frames']:
                        if event.is_set():
                            break
                        print(f"\r{YELLOW}| {frame} | {WHITE}", end='', flush=True)
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
    print("\n" + "~" * 60)


def line_after():
    print("~" * 60 + "\n")


def get_status(status):
    return f"{GREEN}✅{RESET}" if status else f"{RED}🚫{RESET}"


def generation_status(status):
    return f"{LIGHT_GREEN}Получен{WHITE}" if status else f"{RED}Не получен{WHITE}"


def get_games_data():
    with open('Src/data/playground_games_data.json', 'r', encoding='utf-8') as f:
        games_data = json.loads(f.read())
    return games_data


def get_salt(salt):
    try:
        with open('Src/data/salt.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data[salt]

    except Exception as e:
        logging.error(e)



def spinners_table(num_columns=3):
    data = [spinner_name.name for spinner_name in Spinners]

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


def localized_text(key, lang, *args, **kwargs):
    with open('Src/data/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Перевод для указанного языка
    template = translations.get(lang, {}).get(key)

    if template is None:
        # Логирование отсутствующего перевода
        logging.warning(f"No translation available for language code `{lang}` and key `{key}`")

        # Проверка наличия английского перевода
        template = translations.get('en', {}).get(key)
        if template is None:
            logging.warning(f"No English definition found for key `{key}` in translations.json")
            return key  # Возвращаем ключ, если ни одного перевода нет

    try:
        return template.format(**kwargs)
    except:
        return template.format(*args)


print(localized_text('sign_in', lang, LIGHT_GRAY, first_name, last_name, username, WHITE))

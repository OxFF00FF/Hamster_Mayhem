import asyncio
import json
import os
import time

from spinners import Spinners

DEFAULT = '\x1b[39m'
BLACK = '\x1b[30m'
RED = '\x1b[31m'
LIGHT_RED = '\x1b[91m'
GREEN = '\x1b[32m'
LIGHT_GREEN = '\x1b[92m'
YELLOW = '\x1b[33m'
LIGHT_YELLOW = '\x1b[93m'
BLUE = '\x1b[34m'
LIGHT_BLUE = '\x1b[94m'
MAGENTA = '\x1b[35m'
LIGHT_MAGENTA = '\x1b[95m'
CYAN = '\x1b[36m'
LIGHT_CYAN = '\x1b[96m'
WHITE = '\x1b[38;2;%d;%d;%dm' % (200, 200, 200)
LIGHT_WHITE = '\x1b[97m'
LIGHT_GRAY = '\x1b[37m'
DARK_GRAY = '\x1b[90m'
RESET = '\x1b[0m'


def colors_test():
    print(f"{DEFAULT}DEFAULT{RESET}\n"
          f"{BLACK}BLACK{RESET}\n"
          f"{RED}RED{RESET} · "
          f"{LIGHT_RED}LIGHT_RED{RESET}\n"
          f"{GREEN}GREEN{RESET} · "
          f"{LIGHT_GREEN}LIGHT_GREEN{RESET}\n"
          f"{YELLOW}YELLOW{RESET} · "
          f"{LIGHT_YELLOW}LIGHT_YELLOW{RESET}\n"
          f"{BLUE}BLUE{RESET} · "
          f"{LIGHT_BLUE}LIGHT_BLUE{RESET}\n"
          f"{MAGENTA}MAGENTA{RESET} · "
          f"{LIGHT_MAGENTA}LIGHT_MAGENTA{RESET}\n"
          f"{CYAN}CYAN{RESET} · "
          f"{LIGHT_CYAN}LIGHT_CYAN{RESET}\n"
          f"{WHITE}WHITE{RESET} · "
          f"{LIGHT_WHITE}LIGHT_WHITE{RESET}\n"
          f"{LIGHT_GRAY}LIGHT_GRAY{RESET} · "
          f"{DARK_GRAY}DARK_GRAY{RESET}")


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
    {YLW}█████{RST}  {RST}                      ⚡️  Хомячий Беспредел  ⚡️                         {RST}  {YLW}█████{RST}
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


async def loading_v2(event, spinner_name):
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
                        time.sleep(0.3)
        print(f'Spinner `{spinner_name}` not found')
        return


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
    time.sleep(1)
    print(" " + "~" * 60)


def line_after():
    print("\n " + "~" * 60)


def get_status(status):
    return f"{GREEN}✅{RESET}" if status else f"{RED}🚫{RESET}"


def load_settings():
    """Load settings from the JSON file."""
    try:
        with open('data/settings.json', 'r') as file:
            settings = json.load(file)
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return {'send_to_group': False}


def save_settings(settings):
    """Save settings to the JSON file."""
    with open('data/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

import time

BLACK = '\x1b[30m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
MAGENTA = '\x1b[35m'
CYAN = '\x1b[36m'
WHITE = '\x1b[38;2;%d;%d;%dm' % (200, 200, 200)
RESET = '\x1b[0m'

CYN = '\x1b[36m'
YLW = '\x1b[33m'
RST = '\x1b[0m'

banner = f"""
{YLW}     {RST}   {CYN}██╗   ██╗  █████╗  ███╗   ███╗ ███████╗ ████████╗ ███████╗ █████╗  {RST}  {YLW}     {RST}
{YLW}    █{RST}   {CYN}██║   ██║ ██╔══██╗ ████╗ ████║ ██╔════╝ ╚══██╔══╝ ██╔════╝ ██╔══██╗{RST}  {YLW}    █{RST}
{YLW}   ██{RST}   {CYN}████████║ ███████║ ██╔████╔██║ ███████╗    ██║    ███████  ██████╔╝{RST}  {YLW}   ██{RST}
{YLW}  ██ {RST}   {CYN}██╔═══██║ ██╔══██║ ██║╚██╔╝██║ ╚════██║    ██║    ██╔════╝ ██╔══██╗{RST}  {YLW}  ██ {RST}
{YLW} ██  {RST}   {CYN}██║   ██║ ██║  ██║ ██║ ╚═╝ ██║ ███████║    ██║    ███████║ ██║  ██║{RST}  {YLW} ██  {RST}
{YLW}██   {RST}   {CYN}╚═╝   ╚═╝ ╚═╝  ╚═╝ ╚═╝     ╚═╝ ╚══════╝    ╚═╝    ╚══════╝ ╚═╝  ╚═╝{RST}  {YLW}██   {RST}
{YLW}█████{RST}   {RST}                                                                   {RST}  {YLW}█████{RST}
{YLW}   ██{RST}   {RED}███╗   ███╗  █████╗  ██████╗  ███╗   ██╗ ███████╗ ███████╗ ███████╗{RST}  {YLW}   ██{RST}
{YLW}  ██ {RST}   {RED}████╗ ████║ ██╔══██╗ ██╔══██╗ ████╗  ██║ ██╔════╝ ██╔════╝ ██╔════╝{RST}  {YLW}  ██ {RST}
{YLW} ██  {RST}   {RED}██╔████╔██║ ███████║ ██║  ██║ ██╔██╗ ██║ ███████  ███████╗ ███████╗{RST}  {YLW} ██  {RST}
{YLW}██   {RST}   {RED}██║╚██╔╝██║ ██╔══██║ ██║  ██║ ██║╚██╗██║ ██╔════╝ ╚════██║ ╚════██║{RST}  {YLW}██   {RST}
{YLW}█    {RST}   {RED}██║ ╚═╝ ██║ ██║  ██║ ██████╔╝ ██║ ╚████║ ███████║ ███████║ ███████║{RST}  {YLW}█    {RST}
{YLW}     {RST}   {RED}╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚═╝  ╚═══╝ ╚══════╝ ╚══════╝ ╚══════╝{RST}  {YLW}     {RST}
"""


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
    '-': '— • • • • —', '_': '• • — — • —', '"': '• — • • — •', '$': '• • • — • • —', '@': '• — — • — •'
}


def text_to_morse(text: str) -> str:
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

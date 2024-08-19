import logging
from Src.Menu import handle_main_menu_choice, hamster_client, main_menu
from Src.utils import WHITE, RESET, CYAN, line_before, banner, load_settings

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)


def test():
    pass


if __name__ == '__main__':
    settings = load_settings()

    banner()
    hamster_client.login()
    main_menu(settings)

    while True:
        choice = input(f"\nВыберите действие\n{CYAN}(#/1/2/3/4/5/6/$/+/m/0):{RESET} ")
        handle_main_menu_choice(choice, settings)
        line_before()

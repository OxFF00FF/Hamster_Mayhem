import logging
import traceback

from Src.Menu import handle_main_menu_choice, hamster_client, main_menu
from Src.utils import WHITE, RESET, CYAN, line_before, banner

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{RESET}", level=logging.INFO)


def test():
    pass


if __name__ == '__main__':
    banner()
    hamster_client.login()
    main_menu()

    try:
        while True:
            choice = input(f"\nВыберите действие\n{CYAN}(#/1/2/3/4/5/6/$/+/m/0):{RESET} ")
            handle_main_menu_choice(choice)
            line_before()

    except Exception as e:
        logging.error(f"🚫  Произошла ошибка: {e}\n{traceback.format_exc()}\n")

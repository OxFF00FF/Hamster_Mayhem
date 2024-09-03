import logging
import traceback

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Handlers import handle_main_menu_choice
from Src.Login import hamster_client
from Src.Menu import main_menu, main_menu_not_logged
from Src.utils import banner, line_after, localized_text


config = ConfigDB()
lang = config.lang


if __name__ == '__main__':
    # banner()
    hamster_client().login()
    main_menu()

    try:
        while True:
            if config.hamster_token:
                choice = input(f"{DARK_GRAY}{localized_text('choose_action')}:\n{CYAN}(#/1/2/3/4/5/6/a/$/+/s/m/0):{RESET} ")
            else:
                main_menu_not_logged()
                choice = input(f"{DARK_GRAY}{localized_text('choose_action')}:\n{CYAN}(6/m/0):{RESET} ")

            handle_main_menu_choice(choice)
            line_after()

    except Exception as e:
        logging.error(f"{e}\n{traceback.format_exc()}\n")

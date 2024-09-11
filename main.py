import logging
import traceback

from Src.Colors import *
from Src.db_SQlite import ConfigDB
from Src.Handlers import handle_main_menu_choice, handle_main_menu_not_logged_choice
from Src.Login import hamster_client
from Src.Menu import main_menu
from Src.utils import banner, line_after, localized_text, kali

config = ConfigDB()


if __name__ == '__main__':
    try:
        banner()
        hamster_client().login()
        main_menu()

        while True:
            if config.hamster_token:
                # choice = input(f"{DARK_GRAY}{localized_text('choose_action')}\n{CYAN}▶️  (#/1/2/3/4/5/6/a/$/+/s/m/0):{RESET} ")
                choice = input(kali('#/1/2/3/4/5/6/a/$/+/s/m/0'))
                handle_main_menu_choice(choice)

            else:
                # choice = input(f"{DARK_GRAY}{localized_text('choose_action')}\n{CYAN}▶️  (6/0):{RESET} ")
                choice = input(kali('6/0'))
                handle_main_menu_not_logged_choice(choice)

            line_after()

    except Exception as e:
        print(f"🚫  {localized_text('error_occured')}: {e}")
        logging.error(traceback.format_exc())
        exit(1)

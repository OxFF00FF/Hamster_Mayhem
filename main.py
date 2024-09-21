import logging
import traceback

from Src.Handlers import handle_main_menu_choice, handle_main_menu_not_logged_choice
from Src.Menu import main_menu
from Src.utils import banner, line_after, localized_text, kali, check_environment
from Src.Login import HamsterClient as client


def main():
    config = client.user_config
    try:
        banner()
        client.login()
        main_menu()

        while True:
            if config.has_hamster_token:
                choice = input(kali('#/@/1/2/3/4/5/6/a/$/+/s/m/0', '~/Main menu', localized_text('choose_action')))
                handle_main_menu_choice(choice)

            else:
                choice = input(kali('6/s/m/0', '~', localized_text('choose_action')))
                handle_main_menu_not_logged_choice(choice)

            line_after()

    except Exception as e:
        print(f"🚫  {localized_text('error_occured')}: {e}")
        logging.error(traceback.format_exc())
        exit(1)


if __name__ == '__main__':
    check_environment()
    main()

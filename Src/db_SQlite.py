import logging
import os
import sqlite3

from dotenv import load_dotenv

from Src.Colors import *

logging.basicConfig(format=f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{WHITE}\n", level=logging.ERROR)
load_dotenv()


class ConfigDB:
    def __init__(self):
        self.con = sqlite3.connect('Src/data/Config.db', check_same_thread=False)
        self.cur = self.con.cursor()

        self.SET_default_config()
        self.con.commit()

    ####################################################

    # --- CONFIG --- #

    def SET_default_config(self):
        # Настройки по умолчанию
        default_values = {
            'token': '',
            'send_to_group': False,
            'save_to_file': False,
            'apply_promo': False,
            'hamster_token': False,
            'account': 'HAMSTER_TOKEN_1',
            'spinner': 'default',
            'lang': 'ru',
            'bonus_for_one_point': 0,
            'group_url': os.getenv('GROUP_URL'),
            'chat_id': os.getenv('CHAT_ID'),
            'cards_in_top': 10,
            'balance_threshold': 1_000_000,
            'complete_taps': False,
            'complete_tasks': False,
            'complete_cipher': False,
            'complete_minigames': False,
            'complete_combo': False,
            'complete_autobuy_upgrades': False
        }

        self._ADD_missing_values(default_values, 'config')
        if not self.cur.execute('SELECT COUNT(*) FROM config').fetchone()[0]:
            columns = ', '.join(default_values.keys())
            placeholders = ', '.join('?' * len(default_values))
            values = list(default_values.values())

            self.cur.execute(f"INSERT INTO `config` ({columns}) VALUES ({placeholders})", values)
            self.con.commit()
            logging.info("default_config Created")

    def _ADD_missing_values(self, values, table):
        self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        table_exists = self.cur.fetchone()

        if not table_exists:
            self.cur.execute(f'''CREATE TABLE {table} (`uuid` INTEGER PRIMARY KEY AUTOINCREMENT)''')
            self.con.commit()
            logging.info(f"Table '{table}' created")

        self.cur.execute(f"PRAGMA table_info({table})")
        existing_columns = [column[1] for column in self.cur.fetchall()]

        for key, value in values.items():
            if key not in existing_columns:
                column_type = self._get_sqlite_type(value)
                self.cur.execute(f"ALTER TABLE {table} ADD COLUMN `{key}` {column_type}")
                logging.info(f"Added missing column: {key}")

                self.cur.execute(f"UPDATE {table} SET `{key}` = ?", (value,))
                logging.info(f"Updated column: {key}")

        self.con.commit()

    def _get_sqlite_type(self, value):
        if isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'REAL'
        elif isinstance(value, str):
            return 'VARCHAR(255)'
        else:
            return 'TEXT'

    # --- /CONFIG --- #

    ####################################################

    # --- USERS --- #

    def user_exist(self, tg_user_id: int) -> bool:
        self.cur.execute("SELECT COUNT(*) FROM `subscribers` WHERE `tg_user_id` = ?",
                         (tg_user_id,))

        if self.cur.fetchone()[0] > 0:
            return True
        else:
            return False

    def ADD_subscriber(self, account_info: dict):
        tg_user_id = account_info.get('id', 'n/a')
        username = account_info.get('username', 'n/a')
        first_name = account_info.get('firstName', 'n/a')
        account_info['is_subscriber'] = False

        self._ADD_missing_values(account_info, 'subscribers')

        columns = ', '.join(account_info.keys())
        placeholders = ', '.join('?' * len(account_info))
        values = list(account_info.values())

        self.cur.execute(f"INSERT INTO `subscribers` ({columns}) VALUES ({placeholders})", values)
        self.con.commit()

        logging.info(f"""ADD new subscriber: `{first_name} · {username}` id: {tg_user_id} """)

    # --- /USERS --- #

    ####################################################

    # --- PROPERTIES --- #

    def set(self, field_name, value):
        try:
            self.cur.execute(f"UPDATE `config` SET `{field_name}` = ? WHERE `uuid` = 1", (value,))
            self.con.commit()
            logging.info(f"Значение `{field_name}` обновлено на `{value}`")

        except Exception as e:
            logging.error(e)

    def get(self, field_name):
        try:
            self.cur.execute(f"SELECT `{field_name}` FROM `config` WHERE `uuid` = 1")
            result = self.cur.fetchone()

            if result:
                logging.info(f"Значение `{field_name}` получено: `{result[0]}`")
                return result[0]
            else:
                return None

        except Exception as e:
            logging.error(e)

    @property
    def token(self):
        return self.get('token')

    @token.setter
    def token(self, value):
        self.set('token', value)

    @property
    def send_to_group(self):
        return self.get('send_to_group')

    @send_to_group.setter
    def send_to_group(self, value):
        self.set('send_to_group', value)

    @property
    def save_to_file(self):
        return self.get('save_to_file')

    @save_to_file.setter
    def save_to_file(self, value):
        self.set('save_to_file', value)

    @property
    def apply_promo(self):
        return self.get('apply_promo')

    @apply_promo.setter
    def apply_promo(self, value):
        self.set('apply_promo', value)

    @property
    def hamster_token(self):
        return self.get('hamster_token')

    @hamster_token.setter
    def hamster_token(self, value):
        self.set('hamster_token', value)

    @property
    def account(self):
        return self.get('account')

    @account.setter
    def account(self, value):
        self.set('account', value)

    @property
    def spinner(self):
        return self.get('spinner')

    @spinner.setter
    def spinner(self, value):
        self.set('spinner', value)

    @property
    def lang(self):
        return self.get('lang')

    @lang.setter
    def lang(self, value):
        self.set('lang', value)

    @property
    def bonus_for_one_point(self):
        return self.get('bonus_for_one_point')

    @bonus_for_one_point.setter
    def bonus_for_one_point(self, value):
        self.set('bonus_for_one_point', value)

    @property
    def chat_id(self):
        return self.get('chat_id')

    @chat_id.setter
    def chat_id(self, value):
        self.set('chat_id', value)

    @property
    def group_url(self):
        return self.get('group_url')

    @group_url.setter
    def group_url(self, value):
        self.set('group_url', value)

    @property
    def cards_in_top(self):
        return self.get('cards_in_top')

    @cards_in_top.setter
    def cards_in_top(self, value):
        self.set('cards_in_top', value)

    @property
    def balance_threshold(self):
        return self.get('balance_threshold')

    @balance_threshold.setter
    def balance_threshold(self, value):
        self.set('balance_threshold', value)

    @property
    def complete_combo(self):
        return self.get('complete_combo')

    @complete_combo.setter
    def complete_combo(self, value):
        self.set('complete_combo', value)

    @property
    def complete_cipher(self):
        return self.get('complete_cipher')

    @complete_cipher.setter
    def complete_cipher(self, value):
        self.set('complete_cipher', value)

    @property
    def complete_taps(self):
        return self.get('complete_taps')

    @complete_taps.setter
    def complete_taps(self, value):
        self.set('complete_taps', value)

    @property
    def complete_tasks(self):
        return self.get('complete_tasks')

    @complete_tasks.setter
    def complete_tasks(self, value):
        self.set('complete_tasks', value)

    @property
    def complete_minigames(self):
        return self.get('complete_minigames')

    @complete_minigames.setter
    def complete_minigames(self, value):
        self.set('complete_minigames', value)

    @property
    def complete_autobuy_upgrades(self):
        return self.get('complete_autobuy_upgrades')

    @complete_autobuy_upgrades.setter
    def complete_autobuy_upgrades(self, value):
        self.set('complete_autobuy_upgrades', value)

    # --- /PROPERTIES --- #

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

        self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
                           `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                           `send_to_group` INTEGER,
                           `save_to_file` INTEGER,
                           `apply_promo` INTEGER,
                           `hamster_token` INTEGER,
                           `account` VARCHAR(20),
                           `spinner` VARCHAR(20),
                           'lang' VARCHAR(10),
                           'bonus_for_one_point' INTEGER,
                           'group_url' VARCHAR(50),
                           'group_id' VARCHAR(10),
                           `cards_in_top` INTEGER,
                           `balance_threshold` INTEGER
                           )''')
        self.con.commit()
        self._default_config()

    def _default_config(self):
        send_to_group = 0
        save_to_file = 0
        apply_promo = 0
        hamster_token = 0
        account = 'HAMSTER_TOKEN_1'
        spinner = 'default'
        lang = 'ru'
        bonus_for_one_point = 0
        group_url = os.getenv('GROUP_URL')
        group_id = os.getenv('GROUP_ID')
        cards_in_top = 10
        balance_threshold = 1_000_000

        self.cur.execute('SELECT COUNT(*) FROM config')
        count = self.cur.fetchone()[0]
        if count == 0:
            self.cur.execute("INSERT INTO `config`"
                             "(`send_to_group`, `save_to_file`, `apply_promo`, `hamster_token`, `account`, `spinner`, `lang`, `bonus_for_one_point`, `group_url`, `cards_in_top`, `balance_threshold`)"
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (send_to_group, save_to_file, apply_promo, hamster_token, account, spinner, lang, bonus_for_one_point, group_url, group_id, cards_in_top, balance_threshold))

            self.con.commit()
            logging.info(f"default_config Created")

    def set(self, field_name, value):
        try:
            self.cur.execute(f"UPDATE `config` SET `{field_name}` = ? WHERE `id` = 1", (value,))
            self.con.commit()
            logging.info(f"Значение `{field_name}` обновлено на `{value}`")

        except Exception as e:
            logging.error(e)

    def get(self, field_name):
        try:
            self.cur.execute(f"SELECT `{field_name}` FROM `config` WHERE `id` = 1")
            result = self.cur.fetchone()

            if result:
                logging.info(f"Значение `{field_name}` получено: `{result[0]}`")
                return result[0]
            else:
                return None

        except Exception as e:
            logging.error(e)

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
    def group_id(self):
        return self.get('group_id')

    @group_id.setter
    def group_id(self, value):
        self.set('group_id', value)

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

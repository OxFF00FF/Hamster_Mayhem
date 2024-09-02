import logging
import sqlite3

from dotenv import load_dotenv

load_dotenv()


class ConfigDB:
    def __init__(self):
        self.con = sqlite3.connect('Src/data/Config.db')
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
                           'bonus_for_one_point' VARCHAR(10)
                           )''')
        self.con.commit()
        self._default_config()

    def _default_config(self):
        self.cur.execute('SELECT COUNT(*) FROM config')
        count = self.cur.fetchone()[0]
        if count == 0:
            self.cur.execute('''INSERT INTO `config` (`send_to_group`, `save_to_file`, `apply_promo`, `hamster_token`, `account`, `spinner`, `lang`, `bonus_for_one_point`)
                                VALUES (0, 0, 0, 0, 'HAMSTER_TOKEN_1', 'default', 'ru', 0)''')
            self.con.commit()
            logging.info(f"default_config Created")

    def set(self, field_name, value):
        try:
            self.cur.execute(f'''UPDATE `config` SET `{field_name}` = ? WHERE `id` = 1''', (value,))
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
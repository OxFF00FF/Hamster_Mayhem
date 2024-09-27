from sqlalchemy import select

from Src.Logger import set_logger
from database.db import engine, Session
from database.models import Base, User, UserSetting

from config import app_config


def init_db():
    set_logger()
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class SyncORM:

    @staticmethod
    def user_exist(tg_user_id: int) -> tuple or None:
        with Session() as session:
            query = select(User).where(User.tg_user_id == tg_user_id)
            res = session.execute(query)

            result = res.scalar_one_or_none()
            if result:
                return True
            else:
                return False

    @staticmethod
    def ADD_subscriber(user_data: dict):
        with Session() as session:
            new_user = User(**user_data)
            session.add(new_user)
            session.commit()

            default_config = {
                'FK__subscribers_id': new_user.id,
                'account': 'HAMSTER_TOKEN_1',
                'send_to_group': False,
                'save_to_file': False,
                'apply_promo': False,
                'spinner': 'default',
                'lang': 'ru',
                'bonus_for_one_point': 0,
                'group_url': app_config.GROUP_URL,
                'chat_id': int(app_config.CHAT_ID),
                'cards_in_top': 10,
                'all_cards_in_top': False,
                'has_hamster_token': False,

                'balance_threshold': 1_000_000,
                'complete_taps': False,
                'complete_tasks': False,
                'complete_cipher': False,
                'complete_minigames': False,
                'complete_combo': False,
                'complete_autobuy_upgrades': False,
                'complete_promocodes': False
            }

            user_settings = UserSetting(**default_config)
            session.add(user_settings)
            session.commit()


class UserConfig:
    """
    Отвечает за управление настройками конкретного пользователя.
    Инкапсулирует логику доступа к полям настроек и их изменения.
    """

    def __init__(self, user_settings, session):
        self.user_settings = user_settings
        self.session = session

    # ---------- PROPERTIES ---------- #

    @property
    def token(self):
        return self.user_settings.token

    @token.setter
    def token(self, value):
        self.user_settings.token = value
        self.session.commit()

    @property
    def send_to_group(self):
        return self.user_settings.send_to_group

    @send_to_group.setter
    def send_to_group(self, value):
        self.user_settings.send_to_group = value
        self.session.commit()

    @property
    def save_to_file(self):
        return self.user_settings.save_to_file

    @save_to_file.setter
    def save_to_file(self, value):
        self.user_settings.save_to_file = value
        self.session.commit()

    @property
    def apply_promo(self):
        return self.user_settings.apply_promo

    @apply_promo.setter
    def apply_promo(self, value):
        self.user_settings.apply_promo = value
        self.session.commit()

    @property
    def has_hamster_token(self):
        return self.user_settings.has_hamster_token

    @has_hamster_token.setter
    def has_hamster_token(self, value):
        self.user_settings.has_hamster_token = value
        self.session.commit()

    @property
    def account(self):
        return self.user_settings.account

    @account.setter
    def account(self, value):
        self.user_settings.account = value
        self.session.commit()

    @property
    def spinner(self):
        return self.user_settings.spinner

    @spinner.setter
    def spinner(self, value):
        self.user_settings.spinner = value
        self.session.commit()

    @property
    def lang(self):
        return self.user_settings.lang

    @lang.setter
    def lang(self, value):
        self.user_settings.lang = value
        self.session.commit()

    @property
    def bonus_for_one_point(self):
        return self.user_settings.bonus_for_one_point

    @bonus_for_one_point.setter
    def bonus_for_one_point(self, value):
        self.user_settings.bonus_for_one_point = value
        self.session.commit()

    @property
    def chat_id(self):
        return self.user_settings.chat_id

    @chat_id.setter
    def chat_id(self, value):
        self.user_settings.chat_id = value
        self.session.commit()

    @property
    def group_url(self):
        return self.user_settings.group_url

    @group_url.setter
    def group_url(self, value):
        self.user_settings.group_url = value
        self.session.commit()

    @property
    def cards_in_top(self):
        return self.user_settings.cards_in_top

    @cards_in_top.setter
    def cards_in_top(self, value):
        self.user_settings.cards_in_top = value
        self.session.commit()

    @property
    def balance_threshold(self):
        return self.user_settings.balance_threshold

    @balance_threshold.setter
    def balance_threshold(self, value):
        self.user_settings.balance_threshold = value
        self.session.commit()

    @property
    def complete_combo(self):
        return self.user_settings.complete_combo

    @complete_combo.setter
    def complete_combo(self, value):
        self.user_settings.complete_combo = value
        self.session.commit()

    @property
    def complete_cipher(self):
        return self.user_settings.complete_cipher

    @complete_cipher.setter
    def complete_cipher(self, value):
        self.user_settings.complete_cipher = value
        self.session.commit()

    @property
    def complete_taps(self):
        return self.user_settings.complete_taps

    @complete_taps.setter
    def complete_taps(self, value):
        self.user_settings.complete_taps = value
        self.session.commit()

    @property
    def complete_tasks(self):
        return self.user_settings.complete_tasks

    @complete_tasks.setter
    def complete_tasks(self, value):
        self.user_settings.complete_tasks = value
        self.session.commit()

    @property
    def complete_minigames(self):
        return self.user_settings.complete_minigames

    @complete_minigames.setter
    def complete_minigames(self, value):
        self.user_settings.complete_minigames = value
        self.session.commit()

    @property
    def complete_autobuy_upgrades(self):
        return self.user_settings.complete_autobuy_upgrades

    @complete_autobuy_upgrades.setter
    def complete_autobuy_upgrades(self, value):
        self.user_settings.complete_autobuy_upgrades = value
        self.session.commit()

    @property
    def tg_user_id(self):
        return self.user_settings.tg_user_id

    @tg_user_id.setter
    def tg_user_id(self, value):
        self.user_settings.tg_user_id = value
        self.session.commit()

    @property
    def complete_promocodes(self):
        return self.user_settings.complete_promocodes

    @complete_promocodes.setter
    def complete_promocodes(self, value):
        self.user_settings.complete_promocodes = value
        self.session.commit()

    @property
    def all_cards_in_top(self):
        return self.user_settings.all_cards_in_top

    @all_cards_in_top.setter
    def all_cards_in_top(self, value):
        self.user_settings.all_cards_in_top = value
        self.session.commit()

    @property
    def user_name(self):
        return self.user_settings.user_name

    @user_name.setter
    def user_name(self, value):
        self.user_settings.user_name = value
        self.session.commit()

    # ========== PROPERTIES ========== #


class ConfigManager:
    """
    Оотвечает за взаимодействие с базой данных и управление сессиями.
    Извлекает конфигурации пользователей и создает экземпляры UserConfig
    """

    def __init__(self):
        self.session = Session()

    def get_user_config(self, tg_user_id: int):
        user = self.session.query(User).filter_by(tg_user_id=tg_user_id).first()
        if user:
            user_settings = self.session.query(UserSetting).filter_by(FK__subscribers_id=user.id).first()
            if user_settings:
                return UserConfig(user_settings, self.session)
        return None

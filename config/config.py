from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    HAMSTER_TOKEN_1: str
    HAMSTER_TOKEN_2: str
    HAMSTER_TOKEN_3: str

    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: int
    GROUP_URL: str
    BOT_LOGS_GROUP_ID: int

    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str

    @property
    def DB_URL_sqlite(self):
        return f"sqlite:///database/db/Hamster_db.sqlite3"

    model_config = SettingsConfigDict(env_file='.env')


app_config = Config()

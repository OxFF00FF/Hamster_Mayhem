from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Config(BaseSettings):
    HAMSTER_TOKEN_1: str
    HAMSTER_TOKEN_2: Optional[str] = Field(default=None)
    HAMSTER_TOKEN_3: Optional[str] = Field(default=None)

    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None)
    CHAT_ID: Optional[int] = Field(default=None)
    GROUP_URL: Optional[str] = Field(default=None)
    BOT_LOGS_GROUP_ID: Optional[int] = Field(default=None)

    TELEGRAM_API_ID: Optional[str] = Field(default=None)
    TELEGRAM_API_HASH: Optional[str] = Field(default=None)

    @property
    def DB_URL_sqlite(self):
        return f"sqlite:///database/db/Hamster_db.sqlite3"

    model_config = SettingsConfigDict(env_file='.env')


app_config = Config()

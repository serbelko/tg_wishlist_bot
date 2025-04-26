import logging
from dataclasses import dataclass
from pydantic_settings import BaseSettings
from pydantic import Field

from dotenv import load_dotenv
load_dotenv()

from .base import getenv


# logging
def init_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("app.log")


@dataclass
class Bot:
    token: str


@dataclass
class Db:
    url: str


@dataclass
class Channels:
    backup: int


@dataclass
class Config:
    bot: Bot
    db: Db
    channels: Channels


def load_config() -> Config:
    load_dotenv()
    return Config(
        bot=Bot(
            token=getenv("TOKEN"),
        ),
        db=Db(
            url=getenv("DB_URL"),
        ),
        channels=Channels(
            backup=int(getenv("CHANNEL_BACKUP")),
        ),
    )




class Settings(BaseSettings):
    # Настройки бота
    token: str = Field(..., env="TOKEN")

    # Настройки базы данных (используются для подключения к postgres)
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5433, env="POSTGRES_PORT")
    postgres_user: str = Field("postgres", env="POSTGRES_USER")
    postgres_password: str = Field("2284", env="POSTGRES_PASSWORD")
    postgres_db: str = Field("test16", env="POSTGRES_DB")

    # Прочие настройки, например, для каналов
    channel_backup: int = Field(..., env="CHANNEL_BACKUP")
    db_url: str = Field("sqlite+aiosqlite:///main.db", env="DB_URL")
    yandex_folder_id: str = Field(..., env="YANDEX_FOLDER_ID")
    yandex_api_key: str = Field(..., env="YANDEX_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


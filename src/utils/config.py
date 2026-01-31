import os
import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = os.environ.get("TOKEN", "NO_TOKEN")
    BOT_OWNER: str | None = os.environ.get("OWNER")

    TIMEZONE: str = os.environ.get("TIMEZONE", "UTC")

    DATABASE_USER: str = os.environ.get("DATABASE_USER", "user")
    DATABASE_PASSWORD: str = os.environ.get("DATABASE_PASSWORD", "password")
    DATABASE_SERVER: str = os.environ.get("DATABASE_SERVER", "localhost")
    DATABASE_NAME: str = os.environ.get("DATABASE_NAME", "hewo_bot")

    SERVICE_ACCOUNT_FILE: str = os.environ.get("SERVICE_ACCOUNT_FILE", "hewo-481019-92e7aa56882d.json")

    NUM_TRACK_EVENTS: int = int(os.environ.get("NUM_TRACK_EVENTS", "10"))

    class Config:
        case_sensitive = True


settings = Settings()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logger.addHandler(handler)

import asyncio
from sqlmodel import create_engine

from utils.config import settings

# Needed for Alembic migrations
from database.models import * # noqa: F403

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{username}:{password}@{server}/{db}" \
    .format(
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    server=settings.DATABASE_SERVER,
    db=settings.DATABASE_NAME
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_lock = asyncio.Lock()

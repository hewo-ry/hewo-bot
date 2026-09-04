import asyncio

from sqlmodel import create_engine

# Needed for Alembic migrations
from database.models import *
from utils.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_SERVER}/{settings.DATABASE_NAME}" \
    

engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_lock = asyncio.Lock()

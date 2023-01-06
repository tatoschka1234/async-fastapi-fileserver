import sys
from src.core.config import app_settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import logging.config

from src.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

Base = declarative_base()

database_dsn = app_settings.database_dsn

engine = create_async_engine(database_dsn, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

import os
from logging import config as logging_config
from pydantic import BaseSettings

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    user_files_folder = "user_files"
    PROJECT_HOST = os.getenv('PROJECT_HOST', '127.0.0.1')
    PROJECT_PORT: int = int(os.getenv('PROJECT_PORT', '8080'))
    REDIS_URL = "redis://127.0.0.1:6379"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM = "HS256"
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f7f0f4caa6cf63b88e8d3e7"
    UNANE_MAX_LEN: int = 30
    app_title: str = "StorageApp"
    database_dsn: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    database_doker_dsn: str = (
        "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
    )
    database_dsn_test: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/db_tests"
    )
    if os.getenv('RUN_IN_DOCKER'):
        os.environ['DATABASE_DSN'] = database_doker_dsn
        database_dsn = database_doker_dsn
        REDIS_URL = "redis://cache:6379"
    else:
        os.environ['DATABASE_DSN'] = database_dsn

    class Config:
        env_file = './src/.env'


app_settings = AppSettings()

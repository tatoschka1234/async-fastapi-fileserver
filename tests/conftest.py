import asyncio
import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from http import HTTPStatus
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend
from src.cache.cache_redis import redis_cache
from src.main import app
from src.db.db import Base
from src.db.db import get_session


BASE_URL = 'http://127.0.0.1' # todo
REDIS_URL = "redis://127.0.0.1:6379"
TEST_DB_NAME = "db_tests"
database_dsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/db_tests" #todo
#database_dsn = "postgresql+asyncpg://postgres:postgres@db:5432/db_tests"


async def _create_test_db() -> None:
    user, password, database = 'postgres', 'postgres', TEST_DB_NAME
    try:
        await asyncpg.connect(database=database, user=user, password=password)
    except asyncpg.InvalidCatalogNameError:
        conn = await asyncpg.connect(database='postgres', user=user,
                                     password=password)
        await conn.execute(f'CREATE DATABASE "{database}" OWNER "{user}"')
        await conn.close()
        await asyncpg.connect(database=database, user=user, password=password)


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url=BASE_URL) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncGenerator:
    await _create_test_db()
    engine = create_async_engine(database_dsn, echo=True, future=True)
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    rc = RedisCacheBackend(REDIS_URL)
    # TODO
    caches.set(CACHE_KEY, rc)

    async with session() as s:
        def get_session_override():
            return s
        app.dependency_overrides[get_session] = get_session_override
        yield s

    await engine.dispose()
    await close_caches()


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='module')
async def client_authorized() -> AsyncGenerator:
    user, password = "user1", "psw"
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url=BASE_URL) as async_client:
        response = await async_client.post(app.url_path_for("user_register"), json={
            'username': user,
            'password': password
        })
        assert response.status_code == HTTPStatus.CREATED

        response = await async_client.post(app.url_path_for("user_auth"),
                                     data={
                                         'username': user,
                                         'password': password,
                                     })
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.json()
        token = response.json()["access_token"]
        async_client.headers.update({'Authorization': f'Bearer {token}'})
        yield async_client

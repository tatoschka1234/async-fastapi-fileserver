import json
import uuid
from datetime import datetime
from typing import Any

from fastapi_cache import caches
from fastapi_cache.backends.base import BaseCacheBackend
from fastapi_cache.backends.redis import CACHE_KEY
from time import perf_counter


def redis_cache() -> BaseCacheBackend | None:
    return caches.get(CACHE_KEY)


def serialize_data(d: Any) -> Any:
    if isinstance(d, uuid.UUID):
        return str(d)
    if isinstance(d, datetime):
        return d.isoformat()
    return d


async def set_cache(cache, redis_key, data, expire: int = 0) -> None:
    await cache.set(key=redis_key,
                    value=json.dumps(data, default=serialize_data),
                    expire=expire
                    )


async def get_cache(cache: BaseCacheBackend, redis_key: str) -> dict | None:
    result = await cache.get(redis_key)
    if result:
        return json.loads(result)


async def get_key_by_key_pattern(cache: BaseCacheBackend,
                                 pattern: str) -> list:
    client = await cache._client    # :(
    return await client.keys(pattern=pattern)


async def ping(cache: BaseCacheBackend) -> float | str:
    test_key, test_value = "testkey", "testvalue"
    await cache.set(key=test_key, value=test_value, expire=5)
    time_start = perf_counter()
    val = await cache.get(test_key)
    t = perf_counter() - time_start
    if val == test_value:
        return t
    return "Failed to get response from redis"

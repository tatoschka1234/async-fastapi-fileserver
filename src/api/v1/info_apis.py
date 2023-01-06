import sys
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from fastapi_cache.backends.redis import RedisCacheBackend
from src.services.services import files_crud
# from src.db.db import get_session
from src.schemas.files_schema import HealthCheck
# from src.services.urls import url_crud
from src.cache.cache_redis import redis_cache, ping
from src.db.db import get_session

info_router = APIRouter()


@info_router.get('/ping')#, response_model=shorturl_schema.DBHealthModel)
async def get_health(
        db: AsyncSession = Depends(get_session),
        cache: RedisCacheBackend = Depends(redis_cache)) -> HealthCheck:
    cache = await ping(cache)
    db = await files_crud.health(db)
    return HealthCheck(cache=cache, db=db)

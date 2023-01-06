import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1 import user_apis, file_apis, info_apis
from src.core.config import app_settings
#from src.cache.cache_redis import redis_flush_current_db
from fastapi import FastAPI, Request, Response
from sqlalchemy.orm import Session

from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend


app = FastAPI(
    title=app_settings.app_title,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)




@app.on_event('startup')
async def on_startup() -> None:
    rc = RedisCacheBackend(app_settings.REDIS_URL)
    caches.set(CACHE_KEY, rc)


@app.on_event('shutdown')
async def on_shutdown() -> None:
    #await redis_flush_current_db(caches)
    await close_caches()

app.include_router(user_apis.router, prefix="/api/users",
                   tags=["users"])
app.include_router(file_apis.router, prefix="/api/files",
                   tags=["files"])
app.include_router(info_apis.info_router, prefix="/info", tags=["info"])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.PROJECT_HOST,
        port=app_settings.PROJECT_PORT,
    )

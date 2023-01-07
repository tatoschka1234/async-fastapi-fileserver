from datetime import datetime
import uuid
import orjson
from pydantic.main import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FileBase(BaseOrjsonModel):
    id: uuid.UUID
    name: str
    path: str
    created_at: datetime
    is_downloadable: bool
    size: int

    class Config:
        orm_mode = True


class FilesList(BaseOrjsonModel):
    account_id: uuid.UUID
    files: list[FileBase]


class FileSearchResult(BaseOrjsonModel):
    matches: list[FileBase]


class HealthCheck(BaseOrjsonModel):
    db: float
    cache: float


from datetime import datetime
import uuid
from pydantic import BaseModel


class FileBase(BaseModel):
    id: uuid.UUID
    name: str
    path: str
    created_at: datetime
    is_downloadable: bool
    size: int
    class Config:
        orm_mode = True


class FilesList(BaseModel):
    account_id: uuid.UUID
    files: list[FileBase]


class FileSearchResult(BaseModel):
    matches: list[FileBase]


class HealthCheck(BaseModel):
    db: float
    cache: float


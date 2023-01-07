import logging.config
from pathlib import Path
import uuid
from abc import ABC, abstractmethod
from time import perf_counter
from typing import Generic, Type, TypeVar
from sqlalchemy import and_
import aiofiles as aiofiles
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.db import Base
from src.services.auth_utils import get_password_hash
from src.core.logger import LOGGING
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class UserRepository(ABC):
    @abstractmethod
    def user_register(self, *args, **kwargs):
        raise NotImplementedError


class FileRepository(ABC):
    @abstractmethod
    def file_upload(self, *args, **kwargs):
        raise NotImplementedError

    def file_download(self, *args, **kwargs):
        raise NotImplementedError

    def get_files_list(self, *args, **kwargs):
        raise NotImplementedError

    def search(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
UserCreateSchemaType = TypeVar("UserCreateSchemaType", bound=BaseModel)
FileSchemaType = TypeVar("FileSchemaType", bound=BaseModel)
UserType = TypeVar("UserType", bound=Base)


class RepositoryDBUsers(UserRepository, Generic[ModelType, UserCreateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def user_register(self, db: AsyncSession,
                            obj_in: UserCreateSchemaType):
        logger.info(f"Registering user {obj_in.username}")
        psw_hash = get_password_hash(obj_in.password)
        db_obj = self._model(**{"name": obj_in.username,
                              "psw_hash": psw_hash})
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)


class RepositoryDBFiles(FileRepository, Generic[ModelType, FileSchemaType, UserType]):
    def __init__(self, model: Type[ModelType], schema: Type[FileSchemaType]):
        self._model = model
        self._schema = schema

    @staticmethod
    def is_dir_path(path):
        if "." not in path.parts[-1]:
            return True

    async def file_upload(self, db: AsyncSession, *,
                          upload_file: UploadFile,
                          user: UserType,
                          path: Path) -> None:
        try:
            file_path = Path(path)
            if self.is_dir_path(file_path):
                file_path.mkdir(parents=True, exist_ok=True)
                out_file_path = Path(file_path, upload_file.filename)
                logger.debug(f"File path is directory")
            else:
                out_file_path = file_path

            async with aiofiles.open(out_file_path, 'wb') as out_file:
                while content := await upload_file.read(1024):
                    await out_file.write(content)
            size = Path(out_file_path).stat().st_size
            db_obj = self._model(size=size, name=out_file_path.name,
                                 path=str(out_file_path.parent), created_by=user.id)

        finally:
            await upload_file.close()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

    @staticmethod
    def is_valid_uuid(_uuid: str) -> uuid.UUID | None:
        try:
            return uuid.UUID(_uuid, version=4)
        except Exception as e:
            pass

    @staticmethod
    def is_valid_path(p: str) -> Path | None:
        try:
            return Path(p)
        except Exception as e:
            pass

    async def file_download(self, db: AsyncSession,
                            file_id: str, user: UserType) -> File:
        use_uuid = self.is_valid_uuid(file_id)
        if use_uuid:
            logger.debug(f"Download file by uuid")
            statement = select(self._model).where(
                and_(
                    self._model.id == file_id,
                    self._model.created_by == user.id
                )
            )
        elif self.is_valid_path(file_id):
            logger.debug(f"Download file by path")
            file_path = Path(file_id)
            statement = select(self._model).where(
                and_(
                    self._model.path == str(file_path.parent),
                    self._model.name == file_path.name,
                    self._model.created_by == user.id
                )
            )
        result = await db.scalar(statement=statement)
        if result:
            return FileResponse(Path(result.path, result.name))

    async def health(self, db: AsyncSession) -> float:
        statement = select(self._model.name)
        time_start = perf_counter()
        await db.execute(statement=statement)
        return perf_counter() - time_start

    async def get_files_list(self, db: AsyncSession, user: UserType, skip=0,
                             limit=100) -> list[ModelType]:
        statement = select(self._model).where(
            self._model.created_by == user.id).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def search(self, db: AsyncSession, user: UserType, path,
                     ext, order,
                     limit) -> list[FileSchemaType]:
        statement = select(self._model).where(self._model.created_by == user.id)
        if path:
            statement = statement.where(self._model.path == path)
        if ext:
            statement = statement.where(self._model.name.ilike(f'%{ext}%'))
        if limit:
            statement = statement.limit(limit)
        statement = statement.order_by(order)
        results = await db.execute(statement=statement)
        files = results.scalars().all()
        return [self._schema.from_orm(file).dict() for file in files]

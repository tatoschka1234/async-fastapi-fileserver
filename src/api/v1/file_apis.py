from fastapi import (APIRouter, Depends, HTTPException, status, Query, File,
                     UploadFile)
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from fastapi_cache.backends.redis import RedisCacheBackend

from src.db.db import get_session
from src.schemas import files_schema
from src.models.user_model import UserModel
from src.services.services import files_crud
from src.services.auth_utils import get_current_user
from src.cache.cache_redis import (
    redis_cache, set_cache, get_cache,
    get_key_by_key_pattern)


router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    description='File upload',
)
async def upload_file(
    *,
    cache: RedisCacheBackend = Depends(redis_cache),
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    file: UploadFile = File(),
    path: str = Query(example='/src/user_files/', max_length=500, min_length=1)
) -> None:
    """
    File upload.
    """
    if not Path(path).is_absolute():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path should be absolute"
        )
    if path[-1] not in ['/', '\\'] and ("." not in Path(path).parts[-1]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path should be the folder path ending with / or file path with .extension"
        )
    cache_exists = await cache.exists(f'files_{user.id}')
    if cache_exists:
        await cache.delete(f'files_{user.id}')

    keys = await get_key_by_key_pattern(cache, pattern=f'search-user:{user.id}*')
    for key in keys:
        await cache.delete(key)
    await files_crud.file_upload(db=db, upload_file=file, path=path, user=user)


@router.get("/download")
async def get_file(
        *,
        user: UserModel = Depends(get_current_user),
        file_id: str = Query(description='file uuid or path',
                             max_length=500, min_length=1),
        db: AsyncSession = Depends(get_session),
) -> File:
    """
    File download.
    """
    result = await files_crud.file_download(db=db, file_id=file_id, user=user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"file with {file_id=} doesn't exist"
        )
    return result


@router.get("/list", response_model=files_schema.FilesList)
async def get_files(
        *,
        cache: RedisCacheBackend = Depends(redis_cache),
        user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
) -> files_schema.FilesList:
    """
    Get files list.
    """
    result = await get_cache(cache, f'files_{user.id}')
    if not result:
        result = await files_crud.get_files_list(db=db, user=user)
        files_lst = [files_schema.FileBase.from_orm(file).dict() for file in result]

        await set_cache(cache, redis_key=f'files_{user.id}', data={
            'account_id': user.id,
            'files': files_lst
        })
        return files_schema.FilesList(account_id=user.id, files=files_lst)
    return result


@router.get("/search",
            response_model=files_schema.FileSearchResult)
async def files_search(
        *,
        cache: RedisCacheBackend = Depends(redis_cache),
        user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
        path: str = Query(default='', max_length=500),
        extension: str = Query(default='', max_length=10),
        order_by: str = Query(
            default="name",
            max_length=50,
            description=f"{', '.join(list(files_schema.FileBase.__fields__.keys()))}"),
        limit: int = Query(
            default=100,
            ge=1,
            alias='max-size',
            description='Query max size.'
        ),
) -> files_schema.FileSearchResult:
    """
    Search files
    """
    if order_by not in files_schema.FileBase.__fields__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"order_by should be in {files_schema.FileBase.__fields__}"
        )
    cache_key = (f'search-user:{user.id}-path:{path}-ext:{extension}-'
                 f'ord:{order_by}-limit:{limit}')
    result = await get_cache(cache, cache_key)
    if not result:
        result = await files_crud.search(db=db, user=user, path=path,
                                         ext=extension, order=order_by,
                                         limit=limit)
        result = files_schema.FileSearchResult(matches=result)
        await set_cache(cache, redis_key=cache_key, data=result.dict())
    return result



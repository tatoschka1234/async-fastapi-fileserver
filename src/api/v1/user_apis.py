from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from src.core.config import app_settings
from fastapi.security import OAuth2PasswordRequestForm

from src.db.db import get_session
from src.services import auth_utils
from src.services.services import users_crud

from src.schemas import users_schema
router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    description='Register a new user',
    responses={
        400: {
            "model": users_schema.HTTPError,
            "description": "Url already exists in the system",
        }
    }
)
async def user_register(
    *,
    db: AsyncSession = Depends(get_session),
    user: users_schema.UserCreate,
) -> None:
    """
    Register new user.
    """
    await users_crud.user_register(db=db, obj_in=user)


@router.post(
    "/auth",
    response_model=users_schema.Token,
    status_code=status.HTTP_200_OK,
    description='Get auth token',
)
async def user_auth(
    *,
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> users_schema.Token:
    """
    Auth new user.
    """
    user = await auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return users_schema.Token(access_token=access_token)

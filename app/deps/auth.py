from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.deps.misc import get_async_db
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> models.User:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenData(**payload)
    except (JWTError, ValidationError):
        raise creds_exc

    user = await models.User.get(db, uuid=token_data.sub)
    if user is None:
        raise creds_exc

    return user


async def get_active_user(
    user: Annotated[models.User, Depends(get_user)]
) -> models.User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


async def get_active_superuser(
    user: Annotated[models.User, Depends(get_active_user)]
) -> models.User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have the necessary privileges",
        )
    return user

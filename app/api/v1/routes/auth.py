from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.config import settings
from app.security import create_access_token, verify_password

router = APIRouter()


@router.post(
    "/token",
    response_model=schemas.Token,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.ErrorResponse},
    },
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(deps.get_async_db)],
):
    user = await models.User.get(db, username=form_data.username)

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = create_access_token(
        str(user.uuid), settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    "/token/test",
    response_model=schemas.User,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.ErrorResponse},
    },
)
async def test_access_token(
    user: Annotated[models.User, Depends(deps.get_active_user)]
):
    return user

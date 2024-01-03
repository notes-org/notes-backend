from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.User,
    responses={status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse}},
)
async def create_user(
    body: schemas.UserCreate, db: Annotated[AsyncSession, Depends(deps.get_async_db)]
):
    user = await models.User.get(db, username=body.username, email=body.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A user with the same username or email already exists.",
        )

    user = await models.User.create(db, body)
    return user


@router.put(
    "/me",
    response_model=schemas.User,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
async def update_user_me(
    body: schemas.UserUpdate,
    user: Annotated[models.User, Depends(deps.get_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_async_db)],
):
    await user.update(db, body)
    return user


@router.get(
    "/me",
    response_model=schemas.User,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
async def get_user_me(user: Annotated[models.User, Depends(deps.get_active_user)]):
    return user

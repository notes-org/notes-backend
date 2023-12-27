from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas

router = APIRouter()

responses = {404: {"model": schemas.ErrorResponse}}


@router.get("/{username}", response_model=schemas.User, responses=responses)
async def get_user(username: str, db: Annotated[AsyncSession, Depends(deps.get_async_db)]):
    user = await models.User.get_or_404(db, username=username)
    return user
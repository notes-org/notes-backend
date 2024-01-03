import json
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import AnyHttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import deps, models, schemas
from app.utils import hash_url

router = APIRouter()


@router.get("/", response_model=list[schemas.Note])
async def get_notes(
    url: AnyHttpUrl, db: Annotated[AsyncSession, Depends(deps.get_async_db)]
):
    url_hash = hash_url(url)
    query = (
        select(models.Note)
        .join(models.Resource)
        .where(models.Resource.url_hash == url_hash)
    )
    notes = (await db.execute(query)).scalars().all()
    return notes


@router.post(
    "/",
    response_model=schemas.Note,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
async def create_note(
    url: AnyHttpUrl,
    body: schemas.NoteCreate,
    user: Annotated[models.User, Depends(deps.get_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_async_db)],
):
    url_hash = hash_url(url)
    resource = await models.Resource.get_or_404(db, url_hash=url_hash)

    note = models.Note(
        resource_id=resource.id, content=json.dumps(body.content), creator_id=user.id
    )
    await note.save(db)

    return note

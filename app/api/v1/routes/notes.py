import json
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import AnyHttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import deps, models, schemas
from app.utils import hash_url

router = APIRouter()

responses = {404: {"model": schemas.ErrorResponse}}


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


@router.post("/", response_model=schemas.Note, responses=responses)
async def create_note(
    url: AnyHttpUrl,
    body: schemas.NoteCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_db)],
):
    url_hash = hash_url(url)
    resource = await models.Resource.get_or_404(db, url_hash=url_hash)

    note = models.Note(resource_id=resource.id, content=json.dumps(body.content))
    await note.save(db)

    return note

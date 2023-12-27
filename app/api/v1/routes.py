import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AnyHttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import deps, models, schemas
from app.utils import hash_url

router = APIRouter()


responses = {404: {"model": schemas.ErrorResponse}}


@router.get("/users/{username}", response_model=schemas.User, responses=responses)
async def get_user(username: str, db: Annotated[AsyncSession, Depends(deps.get_async_db)]):
    user = await models.User.get_or_404(db, username=username)
    return user


@router.get(
    "/resources",
    response_model=schemas.Resource | list[schemas.Resource],
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_resource_or_resources(
    db: Annotated[AsyncSession, Depends(deps.get_async_db)],
    url: Annotated[AnyHttpUrl | None, None] = None,
):
    if url:
        # Return a single resource
        url_hash = hash_url(url)
        resource = await models.Resource.get_or_404(
            db, select_related=["notes"], url_hash=url_hash
        )
        return resource
    else:
        # Return a list of resources
        resources = await models.Resource.get_list(db, select_related=["notes"])
        return resources


@router.post(
    "/resources",
    response_model=schemas.Resource,
    response_model_exclude_unset=True,
    responses={409: {"model": schemas.ErrorResponse}},
)
async def create_resource(
    url: AnyHttpUrl, db: Annotated[AsyncSession, Depends(deps.get_async_db)]
):
    try:
        resource = await models.Resource.create(db, url)
    except IntegrityError:
        raise HTTPException(status_code=409, detail=f"Resource already exists: {url}")

    resource = await models.Resource.get(
        db, select_related=["notes"], uuid=resource.uuid
    )
    return resource


@router.get("/notes", response_model=list[schemas.Note])
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
    "/notes",
    response_model=schemas.Note,
    responses=responses,
)
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

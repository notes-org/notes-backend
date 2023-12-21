import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AnyHttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import deps, models, schemas
from app.utils import hash_url

router = APIRouter()


responses = {404: {"model": schemas.ErrorResponse}}


@router.get("/users/{username}", response_model=schemas.User, responses=responses)
def get_user(username: str, db: Annotated[Session, Depends(deps.get_db)]):
    user = models.User.get_or_404(db, username=username)
    return user


@router.get(
    "/resources",
    response_model=schemas.Resource | list[schemas.Resource],
    response_model_exclude_unset=True,
    responses=responses,
)
def get_resource_or_resources(
    url: Annotated[AnyHttpUrl | None, None], db: Annotated[Session, Depends(deps.get_db)]
):
    if url:
        # Return a single resource
        url_hash = hash_url(url)
        resource = models.Resource.get_or_404(
            db, select_related=["notes"], url_hash=url_hash
        )
        return resource

    # Return a list of resources
    resources = models.Resource.get_list(db, select_related=["notes"])
    return resources


@router.post(
    "/resources",
    response_model=schemas.Resource,
    response_model_exclude_unset=True,
    responses={409: {"model": schemas.ErrorResponse}},
)
def create_resource(url: AnyHttpUrl, db: Annotated[Session, Depends(deps.get_db)]):
    try:
        resource = models.Resource.create(db, url)
    except IntegrityError:
        raise HTTPException(status_code=409, detail=f"Resource already exists: {url}")

    return resource


@router.get("/notes", response_model=list[schemas.Note])
def get_notes(url: AnyHttpUrl, db: Annotated[Session, Depends(deps.get_db)]):
    url_hash = hash_url(url)
    notes = (
        db.query(models.Note)
        .join(models.Resource)
        .filter(models.Resource.url_hash == url_hash)
        .all()
    )
    return notes


@router.post(
    "/notes",
    response_model=schemas.Note,
    responses=responses,
)
def create_note(
    url: AnyHttpUrl, body: schemas.NoteCreate, db: Annotated[Session, Depends(deps.get_db)]
):
    url_hash = hash_url(url)
    resource = models.Resource.get_or_404(db, url_hash=url_hash)

    note = models.Note(resource_id=resource.id, content=json.dumps(body.content))
    note.save(db)

    return note

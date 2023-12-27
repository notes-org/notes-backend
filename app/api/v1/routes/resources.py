from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AnyHttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.utils import hash_url

router = APIRouter()

responses = {404: {"model": schemas.ErrorResponse}}


@router.get(
    "/",
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
    "/",
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

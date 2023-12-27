from fastapi import APIRouter

from .routes import notes, resources, users

v1_router = APIRouter()


v1_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
v1_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
v1_router.include_router(users.router, prefix="/users", tags=["Users"])
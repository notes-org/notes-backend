import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1
from app.config import settings

app = FastAPI(title="Notes", debug=settings.DEBUG)


@app.on_event("startup")
def create_logger():
    level = settings.LOGLEVEL.upper()

    handler = logging.StreamHandler()
    handler.setLevel(level)

    logger = logging.getLogger("app")
    logger.setLevel(level)
    logger.addHandler(handler)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API routes
app.include_router(v1.router, prefix="/v1")

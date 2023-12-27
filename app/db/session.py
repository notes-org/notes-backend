from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

_db_url = settings.POSTGRES_DSN
_async_db_url = settings.POSTGRES_DSN.replace("://", "+asyncpg://")

engine = create_engine(url=_db_url)
async_engine = create_async_engine(url=_async_db_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Do not reload from DB after commit
)

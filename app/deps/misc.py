from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal, AsyncSessionLocal


def get_db() -> Generator:
    with SessionLocal() as db_session:
        yield db_session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db_session:
        yield db_session

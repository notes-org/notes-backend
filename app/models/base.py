from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload, Session

from app.db.declarative_base import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    async def get(
        cls, db: AsyncSession, select_related: list[str] | None = None, **kwargs
    ):
        select_related = select_related if select_related else []
        query = select(cls)

        for field, value in kwargs.items():
            query = query.where(getattr(cls, field) == value)

        for related_field in select_related:
            query = query.options(joinedload(getattr(cls, related_field)))

        return (await db.execute(query.limit(1))).scalars().first()

    @classmethod
    async def get_or_404(
        cls, db: AsyncSession, select_related: list[str] | None = None, **kwargs
    ):
        obj = await cls.get(db, select_related, **kwargs)

        if obj is None:
            raise HTTPException(
                status_code=404, detail=f"{cls.__name__} object could not be found"
            )

        return obj

    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        select_related: list[str] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        **kwargs,
    ):
        select_related = select_related if select_related else []
        query = select(cls)

        for field, value in kwargs.items():
            if isinstance(value, set):
                # Filter by each value in the set
                query = query.where(getattr(cls, field).in_(value))
            else:
                query = query.where(getattr(cls, field) == value)

        for related_field in select_related:
            query = query.options(selectinload(getattr(cls, related_field)))

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return (await db.execute(query)).scalars().all()

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()

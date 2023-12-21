from fastapi import HTTPException
from sqlalchemy.orm import joinedload, Session

from app.db.declarative_base import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def get(cls, db: Session, select_related: list[str] | None = None, **kwargs):
        select_related = select_related if select_related else []
        query = db.query(cls)

        for field, value in kwargs.items():
            query = query.filter(getattr(cls, field) == value)

        for related_field in select_related:
            query = query.options(joinedload(getattr(cls, related_field)))

        return query.one_or_none()

    @classmethod
    def get_list(
        cls,
        db: Session,
        select_related: list[str] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        **kwargs,
    ):
        select_related = select_related if select_related else []
        query = db.query(cls)

        for field, value in kwargs.items():
            if isinstance(value, set):
                # Filter by each value in the set
                query = query.filter(getattr(cls, field).in_(value))
            else:
                query = query.filter(getattr(cls, field) == value)

        for related_field in select_related:
            query = query.options(joinedload(getattr(cls, related_field)))

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query.all()

    @classmethod
    def get_or_404(cls, db: Session, select_related: list[str] | None = None, **kwargs):
        obj = cls.get(db, select_related, **kwargs)

        if obj is None:
            raise HTTPException(
                status_code=404, detail=f"{cls.__name__} object could not be found"
            )

        return obj

    @classmethod
    def get_or_create(cls, db: Session, **kwargs):
        obj = cls.get(db, **kwargs)

        if obj is None:
            obj = cls(**kwargs)
            obj.save(db)
            db.refresh(obj)

        return obj

    def save(self, db: Session):
        db.add(self)
        db.commit()

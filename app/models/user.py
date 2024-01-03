import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship


from app import schemas
from app.models.base import Base
from app.security import get_password_hash
from app.utils import setattrs


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("Note", back_populates="creator")

    @classmethod
    async def create(cls, db: AsyncSession, data: schemas.UserCreate):
        user = cls(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
        )
        await user.save(db)
        await db.refresh(user)
        return user
    
    async def update(self, db: AsyncSession, data: schemas.UserUpdate):
        data_dict = data.dict(exclude_unset=True)
        if data_dict["password"]:
            hashed_password = get_password_hash(data.password)
            del data_dict["password"]
            data_dict["hashed_password"] = hashed_password

        setattrs(self, **data_dict)

        await self.save(db)
        await db.refresh(self)
        
        

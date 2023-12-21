import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    # TODO: Set nullable=False when auth is fully implemented
    creator_id = Column(Integer, ForeignKey("users.id"))

    resource = relationship("Resource", foreign_keys=[resource_id], back_populates="notes")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="notes")

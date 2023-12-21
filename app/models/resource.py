import logging
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.scraper import Scraper
from app.utils import hash_url
from app.models.base import Base

logger = logging.getLogger("app")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    url = Column(String, nullable=False)
    url_hash = Column(String, nullable=False, unique=True, index=True)
    tld = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    favicon_url = Column(String)
    site_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("Note", back_populates="resource")

    @classmethod
    def create(cls, db: Session, url: str):
        scraper = Scraper()
        try:
            data = scraper.scrape_page(url)
        except Exception as e:
            logger.debug(f"Failed to scrape: {e}")
            raise HTTPException(status_code=500)
        
        resource = cls(
            url=url,
            url_hash=hash_url(url),
            tld=data["tld"],
            title=data["title"],
            description=data["description"],
            image_url=data["image_url"],
            favicon_url=data["favicon_url"],
            site_name=data["site_name"]
        )
        resource.save(db)

        return resource
    
    @classmethod
    def get_or_create(cls, db: Session, url: str):
        url_hash = hash_url(url)
        resource = cls.get(db, url_hash=url_hash)

        if resource is None:
            try:
                cls.create(db, url)
            except Exception:
                db.rollback()
                resource = cls.get(db, url_hash=url_hash)

        return resource
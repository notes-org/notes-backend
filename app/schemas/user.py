import datetime
import uuid

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode=True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class User(UserBase):
    uuid: uuid.UUID
    is_active: bool = True
    created_at: datetime.datetime
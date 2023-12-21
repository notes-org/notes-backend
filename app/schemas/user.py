import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    auth0_sub: str
    username: str
    email: str

    class Config:
        orm_mode=True


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase):
    created_at: datetime.datetime
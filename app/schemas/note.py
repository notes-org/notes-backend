import datetime

from pydantic import BaseModel, Json


class NoteBase(BaseModel):
    content: Json

    class Config:
        orm_mode = True


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class Note(NoteBase):
    created_at: datetime.datetime

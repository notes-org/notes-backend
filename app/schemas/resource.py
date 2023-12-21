from pydantic import AnyHttpUrl, BaseModel, root_validator

from app.schemas.note import Note
from app.utils import get_favicon_url


class ResourceBase(BaseModel):
    url: AnyHttpUrl
    tld: str
    title: str
    description: str | None = None
    image_url: AnyHttpUrl | None = None
    favicon_url: AnyHttpUrl | None = None
    site_name: str | None = None

    class Config:
        orm_mode = True


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(ResourceBase):
    pass


class Resource(ResourceBase):
    notes: list[Note]

    @root_validator
    def get_google_favicon_url(cls, values: dict):
        tld = values.get("tld")
        if tld:
            values["favicon_url"] = get_favicon_url(tld)
        return values
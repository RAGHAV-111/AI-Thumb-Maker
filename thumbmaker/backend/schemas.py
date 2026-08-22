from datetime import datetime

from pydantic import BaseModel


class ThumbnailCreate(BaseModel):
    title: str
    prompt: str


class ThumbnailOut(BaseModel):
    id: int
    title: str
    prompt: str
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class FolderOut(CamelModel):
    id: str
    name: str
    created_at: datetime


class FolderIn(CamelModel):
    name: str = Field(min_length=1, max_length=100)

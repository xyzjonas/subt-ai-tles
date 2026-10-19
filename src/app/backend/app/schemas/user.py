from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class UserOut(CamelModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool
    created_at: datetime


class UserCreate(CamelModel):
    username: str = Field(min_length=1, max_length=64, pattern=r"^\S+$")
    password: str = Field(min_length=8, max_length=256)
    is_admin: bool = False


class UserUpdate(CamelModel):
    password: str | None = Field(default=None, min_length=8, max_length=256)
    is_admin: bool | None = None
    is_active: bool | None = None

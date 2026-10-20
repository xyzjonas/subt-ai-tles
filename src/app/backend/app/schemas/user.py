from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import CamelModel

Locale = Literal["en", "cs"]


class UserOut(CamelModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool
    must_change_password: bool
    monthly_quota: int
    locale: Locale | None = None
    created_at: datetime


class UserCreate(CamelModel):
    username: str = Field(min_length=1, max_length=64, pattern=r"^\S+$")
    password: str = Field(min_length=8, max_length=256)
    is_admin: bool = False
    monthly_quota: int | None = Field(default=None, ge=0)
    locale: Locale | None = None


class UserUpdate(CamelModel):
    password: str | None = Field(default=None, min_length=8, max_length=256)
    is_admin: bool | None = None
    is_active: bool | None = None
    monthly_quota: int | None = Field(default=None, ge=0)


class ProfileUpdate(CamelModel):
    """What users change about themselves; `locale: null` follows the browser again."""

    locale: Locale | None


class PasswordChange(CamelModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=256)

from datetime import datetime

from pydantic import Field, field_validator

from app.models import MembershipRequestStatus
from app.schemas.base import CamelModel

# The email becomes the username, which is capped at 64 characters.
MAX_EMAIL_LENGTH = 64
MAX_DETAILS_LENGTH = 1000


class MembershipRequestCreate(CamelModel):
    email: str = Field(
        min_length=3, max_length=MAX_EMAIL_LENGTH, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    details: str | None = Field(default=None, max_length=MAX_DETAILS_LENGTH)

    @field_validator("email")
    @classmethod
    def _lowercase(cls, value: str) -> str:
        return value.lower()

    @field_validator("details")
    @classmethod
    def _blank_is_none(cls, value: str | None) -> str | None:
        return value.strip() or None if value else None


class MembershipRequestOut(CamelModel):
    id: int
    email: str
    details: str | None
    status: MembershipRequestStatus
    created_at: datetime
    decided_at: datetime | None


class MembershipRequestApprove(CamelModel):
    """The temporary password the admin hands over; the new user must replace it."""

    password: str = Field(min_length=8, max_length=256)

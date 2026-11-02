from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, UtcDateTime


class MembershipRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MembershipRequest(Base):
    """Someone asking for an account; an admin approves or rejects it by hand."""

    __tablename__ = "membership_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Becomes the username on approval.
    email: Mapped[str] = mapped_column(index=True)
    details: Mapped[str | None]
    status: Mapped[MembershipRequestStatus] = mapped_column(
        Enum(
            MembershipRequestStatus,
            native_enum=False,
            length=16,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=MembershipRequestStatus.PENDING,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime, default=lambda: datetime.now(UTC)
    )
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime)

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import DEFAULT_MONTHLY_QUOTA
from app.db import Base, UtcDateTime

if TYPE_CHECKING:
    from app.models.job import Job


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Set while the password is a temporary one an admin handed out.
    must_change_password: Mapped[bool] = mapped_column(
        default=False, server_default=sa.false()
    )
    # UI language; None means "follow the browser".
    locale: Mapped[str | None] = mapped_column(default=None)
    # Credits per calendar month (UTC).
    monthly_quota: Mapped[int] = mapped_column(
        default=DEFAULT_MONTHLY_QUOTA, server_default=str(DEFAULT_MONTHLY_QUOTA)
    )
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime, default=lambda: datetime.now(UTC)
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )

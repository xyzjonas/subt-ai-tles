import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, UtcDateTime

if TYPE_CHECKING:
    from app.models.job import Job


class Folder(Base):
    """A user-made group of requests, e.g. all episodes of one show."""

    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid.uuid4().hex)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime, default=lambda: datetime.now(UTC)
    )

    # deleting a folder only ungroups its requests (the FK is SET NULL)
    jobs: Mapped[list["Job"]] = relationship(back_populates="folder", passive_deletes=True)

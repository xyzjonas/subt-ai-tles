import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, UtcDateTime

if TYPE_CHECKING:
    from app.models.cue import Cue
    from app.models.user import User


class JobStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobStage(StrEnum):
    """Where a processing job currently is. `recognizing` also covers waiting in the queue."""

    RECOGNIZING = "recognizing"
    SUMMARIZING = "summarizing"
    TRANSLATING = "translating"


def _now() -> datetime:
    return datetime.now(UTC)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid.uuid4().hex)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    file_name: Mapped[str]
    source_lang: Mapped[str] = mapped_column(ForeignKey("languages.code"))
    target_lang: Mapped[str] = mapped_column(ForeignKey("languages.code"))
    cue_count: Mapped[int]
    status: Mapped[JobStatus] = mapped_column(
        Enum(
            JobStatus,
            native_enum=False,
            length=16,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=JobStatus.PROCESSING,
    )
    processed_cues: Mapped[int] = mapped_column(default=0)
    stage: Mapped[JobStage] = mapped_column(
        Enum(
            JobStage,
            native_enum=False,
            length=16,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=JobStage.RECOGNIZING,
        server_default=JobStage.RECOGNIZING.value,
    )
    # SummaryStatus of the story brief, once known
    summary_status: Mapped[str | None]
    model: Mapped[str | None]
    confidence: Mapped[float | None]
    error: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now, onupdate=_now)

    owner: Mapped["User"] = relationship(back_populates="jobs")
    cues: Mapped[list["Cue"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Cue.index",
    )

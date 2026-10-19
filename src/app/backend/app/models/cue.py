from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.job import Job


class Cue(Base):
    __tablename__ = "cues"
    __table_args__ = (UniqueConstraint("job_id", "idx"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    # 1-based position in the .srt file.
    index: Mapped[int] = mapped_column("idx")
    # Offsets in milliseconds.
    start: Mapped[int] = mapped_column("start_ms")
    end: Mapped[int] = mapped_column("end_ms")
    source: Mapped[str]
    target: Mapped[str] = mapped_column(default="")

    job: Mapped["Job"] = relationship(back_populates="cues")

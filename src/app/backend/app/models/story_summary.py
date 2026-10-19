from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, UtcDateTime


def _now() -> datetime:
    return datetime.now(UTC)


class StorySummary(Base):
    """Concise story brief of a recognized title, reused as translation context.

    The key identifies the media (e.g. `tv:the-office:s02e05`), not the language pair.
    """

    __tablename__ = "story_summaries"

    key: Mapped[str] = mapped_column(primary_key=True)
    summary: Mapped[str]
    model: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now)

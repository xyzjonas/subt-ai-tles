from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, UtcDateTime


class UsageKind(StrEnum):
    TRANSLATE = "translate"
    RETRANSLATE = "retranslate"
    SUMMARIZE = "summarize"


def _now() -> datetime:
    return datetime.now(UTC)


class UsageRecord(Base):
    """Tokens one request consumed. Survives its job (cancelled jobs still cost tokens)."""

    __tablename__ = "usage_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))
    kind: Mapped[UsageKind] = mapped_column(
        Enum(
            UsageKind,
            native_enum=False,
            length=16,
            values_callable=lambda enum: [member.value for member in enum],
        )
    )
    model: Mapped[str]
    prompt_tokens: Mapped[int]
    completion_tokens: Mapped[int]
    # Frozen at spend time, so later rate changes don't rewrite history.
    credits: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, default=_now, index=True)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class ModelRate(Base):
    """Admin-configurable credit cost of an offered model, per 1,000 tokens."""

    __tablename__ = "model_rates"

    model: Mapped[str] = mapped_column(primary_key=True)
    input_credits_per_1k: Mapped[float]
    output_credits_per_1k: Mapped[float]

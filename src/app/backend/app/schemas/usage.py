from datetime import date, datetime

from pydantic import Field

from app.models import UsageKind
from app.schemas.base import CamelModel


class UsageRecordOut(CamelModel):
    id: int
    kind: UsageKind
    model: str
    job_id: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    credits: float
    created_at: datetime


class UsageBucket(CamelModel):
    """Usage of one day, ISO week (starting Monday) or month; `start` is its first day."""

    start: date
    requests: int
    tokens: int
    credits: float


class QuotaOut(CamelModel):
    limit: int
    used: float
    remaining: float


class UsageSummary(CamelModel):
    quota: QuotaOut
    daily: list[UsageBucket]
    weekly: list[UsageBucket]
    monthly: list[UsageBucket]


class ModelRateIn(CamelModel):
    input_credits_per_1k: float = Field(ge=0)
    output_credits_per_1k: float = Field(ge=0)


class ModelRateOut(ModelRateIn):
    model: str

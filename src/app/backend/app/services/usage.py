"""Token usage: what requests consumed, what that costs in credits and the monthly quota."""

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from subtaitles import Usage  # type: ignore[import-untyped]

from app.errors import InvalidInputError, QuotaExceededError
from app.models import ModelRate, UsageKind, UsageRecord, User
from app.schemas import ModelRateIn, QuotaOut, UsageBucket, UsageSummary

_DAYS = 30
_WEEKS = 12
_MONTHS = 12


def _month_start(day: date) -> date:
    return day.replace(day=1)


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _shift_months(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def _utc_midnight(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=UTC)


def _today() -> date:
    return datetime.now(UTC).date()


def list_rates(db: Session) -> list[ModelRate]:
    return list(db.scalars(select(ModelRate).order_by(ModelRate.model)))


def rate_for(db: Session, model: str) -> ModelRate:
    rate = db.get(ModelRate, model)
    if rate is None:
        msg = f"Model {model} is not offered"
        raise InvalidInputError(msg)
    return rate


def set_rate(db: Session, model: str, data: ModelRateIn) -> ModelRate:
    rate = db.get(ModelRate, model)
    if rate is None:
        rate = ModelRate(model=model)
        db.add(rate)
    rate.input_credits_per_1k = data.input_credits_per_1k
    rate.output_credits_per_1k = data.output_credits_per_1k
    db.flush()
    return rate


def credits_for(rate: ModelRate, usage: Usage) -> float:
    return (
        usage.prompt_tokens * rate.input_credits_per_1k
        + usage.completion_tokens * rate.output_credits_per_1k
    ) / 1000


def record(  # noqa: PLR0913
    db: Session,
    *,
    user_id: int,
    job_id: str | None,
    kind: UsageKind,
    model: str,
    usage: Usage,
) -> UsageRecord | None:
    """Store what a request consumed. Nothing is stored for requests that used no tokens."""
    if usage.total_tokens == 0:
        return None
    entry = UsageRecord(
        user_id=user_id,
        job_id=job_id,
        kind=kind,
        model=model,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        credits=credits_for(rate_for(db, model), usage),
    )
    db.add(entry)
    db.flush()
    return entry


def used_this_month(db: Session, user: User) -> float:
    since = _utc_midnight(_month_start(_today()))
    return (
        db.scalar(
            select(func.coalesce(func.sum(UsageRecord.credits), 0.0)).where(
                UsageRecord.user_id == user.id, UsageRecord.created_at >= since
            )
        )
        or 0.0
    )


def quota(db: Session, user: User) -> QuotaOut:
    used = used_this_month(db, user)
    return QuotaOut(
        limit=user.monthly_quota, used=used, remaining=max(0.0, user.monthly_quota - used)
    )


def ensure_within_quota(db: Session, user: User) -> None:
    if used_this_month(db, user) >= user.monthly_quota:
        msg = "Monthly quota exceeded"
        raise QuotaExceededError(msg)


def _buckets(
    rows: list[tuple[datetime, int, float]],
    *,
    first: date,
    count: int,
    start_of: Callable[[date], date],
    step: Callable[[date], date],
) -> list[UsageBucket]:
    """Oldest-first buckets from `first`, including empty ones so charts have no gaps."""
    totals: dict[date, list[float]] = {}
    day = first
    for _ in range(count):
        totals[day] = [0, 0, 0.0]
        day = step(day)
    for created_at, tokens, cost in rows:
        bucket = totals.get(start_of(created_at.date()))
        if bucket is not None:
            bucket[0] += 1
            bucket[1] += tokens
            bucket[2] += cost
    return [
        UsageBucket(start=start, requests=int(n), tokens=int(tokens), credits=cost)
        for start, (n, tokens, cost) in totals.items()
    ]


def summary(db: Session, user: User) -> UsageSummary:
    today = _today()
    first_day = today - timedelta(days=_DAYS - 1)
    first_week = _week_start(today) - timedelta(weeks=_WEEKS - 1)
    first_month = _shift_months(_month_start(today), -(_MONTHS - 1))
    oldest = min(first_day, first_week, first_month)
    rows = [
        (created_at, prompt + completion, cost)
        for created_at, prompt, completion, cost in db.execute(
            select(
                UsageRecord.created_at,
                UsageRecord.prompt_tokens,
                UsageRecord.completion_tokens,
                UsageRecord.credits,
            ).where(
                UsageRecord.user_id == user.id,
                UsageRecord.created_at >= _utc_midnight(oldest),
            )
        )
    ]
    return UsageSummary(
        quota=quota(db, user),
        daily=_buckets(
            rows,
            first=first_day,
            count=_DAYS,
            start_of=lambda d: d,
            step=lambda d: d + timedelta(days=1),
        ),
        weekly=_buckets(
            rows,
            first=first_week,
            count=_WEEKS,
            start_of=_week_start,
            step=lambda d: d + timedelta(weeks=1),
        ),
        monthly=_buckets(
            rows,
            first=first_month,
            count=_MONTHS,
            start_of=_month_start,
            step=lambda d: _shift_months(d, 1),
        ),
    )


def list_records(db: Session, user: User, limit: int, offset: int) -> list[UsageRecord]:
    return list(
        db.scalars(
            select(UsageRecord)
            .where(UsageRecord.user_id == user.id)
            .order_by(UsageRecord.created_at.desc(), UsageRecord.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )

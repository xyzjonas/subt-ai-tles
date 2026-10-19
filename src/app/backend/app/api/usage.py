from typing import Annotated

from fastapi import APIRouter, Query

from app.db import DbDep
from app.schemas import UsageRecordOut, UsageSummary
from app.security import CurrentUser
from app.services import usage

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("")
def get_usage(db: DbDep, user: CurrentUser) -> UsageSummary:
    return usage.summary(db, user)


@router.get("/records")
def list_records(
    db: DbDep,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UsageRecordOut]:
    records = usage.list_records(db, user, limit, offset)
    return [UsageRecordOut.model_validate(r) for r in records]

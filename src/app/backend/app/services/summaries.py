"""Persistence of story briefs, plugged into `subtaitles` as its summary store."""

import logging

from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import StorySummary

logger = logging.getLogger(__name__)


class SummaryStore:
    """DB-backed `SummaryStoreProtocol`.

    Uses its own short sessions, so a stored brief is committed immediately and survives a
    failed or cancelled job (it already cost tokens).
    """

    def __init__(self, model: str) -> None:
        self.model = model

    async def get(self, key: str) -> str | None:
        with SessionLocal() as db:
            row = db.get(StorySummary, key)
            return row.summary if row else None

    async def put(self, key: str, summary: str) -> None:
        with SessionLocal() as db:
            try:
                db.add(StorySummary(key=key, summary=summary, model=self.model))
                db.commit()
            except IntegrityError:
                # a concurrent job stored the same title first; keep that one
                db.rollback()
                logger.info("Story brief for %s already stored", key)

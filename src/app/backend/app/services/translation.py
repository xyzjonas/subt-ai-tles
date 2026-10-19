"""Translation business logic: the Celery job body and the inline retranslate.

The heavy lifting is done by `subtaitles`; this module maps jobs/cues to and from it and
reports progress to the database, which is what the UI polls.
"""

import asyncio
import contextlib
import logging
from functools import cache

import diskcache  # type: ignore[import-untyped]
from openai import AuthenticationError, RateLimitError
from pysrt import SubRipFile, SubRipItem, SubRipTime  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.orm import Session
from subtaitles import (  # type: ignore[import-untyped]
    Lang,
    OpenAiTranslator,
    ProgressData,
    translate_srt,
)

from app.config import settings
from app.db import SessionLocal
from app.errors import UpstreamError
from app.models import Cue, Job, JobStatus
from app.schemas import CueVariant, JobEstimate

logger = logging.getLogger(__name__)

_POLL_SECONDS = 0.5
_CONTEXT_CUES = 2


@cache
def _cache() -> diskcache.Cache | None:
    return diskcache.Cache(settings.srt_cache_dir) if settings.srt_cache_dir else None


def make_translator() -> OpenAiTranslator:
    """Build a fresh translator per use: its HTTP client is bound to the running event loop."""
    return OpenAiTranslator(
        model=settings.openai_model,
        openapi_key=settings.openai_api_key,
        openapi_org=settings.openai_org_id,
        cache=_cache(),
    )


def estimate(cue_count: int) -> JobEstimate:
    return JobEstimate(seconds=max(5, round(cue_count / 24)), tokens=cue_count * 5)


def detect_language(content: bytes) -> str:  # noqa: ARG001
    """Return the detected language. PLACEHOLDER: always English."""
    return "en"


def retranslate_cue(db: Session, cue: Cue, prompt: str | None) -> list[CueVariant]:
    job = db.get(Job, cue.job_id)
    if job is None:
        msg = "Job not found"
        raise UpstreamError(msg)
    neighbours = list(
        db.scalars(
            select(Cue)
            .where(
                Cue.job_id == cue.job_id,
                Cue.index.between(cue.index - _CONTEXT_CUES, cue.index + _CONTEXT_CUES),
                Cue.index != cue.index,
            )
            .order_by(Cue.index)
        )
    )
    try:
        variants = asyncio.run(
            make_translator().retranslate(
                cue.source,
                source=Lang(job.source_lang),
                target=Lang(job.target_lang),
                prompt=prompt,
                context_before=[c.source for c in neighbours if c.index < cue.index],
                context_after=[c.source for c in neighbours if c.index > cue.index],
            )
        )
    except Exception as exc:
        logger.exception("Retranslating cue %s of job %s failed", cue.index, cue.job_id)
        msg = _user_message(exc)
        raise UpstreamError(msg) from exc
    return [CueVariant(label=v.label, text=v.text) for v in variants]


def _user_message(exc: Exception) -> str:
    """Short, user-facing reason. Details (which may include key fragments) stay in the log."""
    if isinstance(exc, AuthenticationError):
        return "The translation service is not configured correctly"
    if isinstance(exc, RateLimitError):
        return "The translation service is busy, please try again later"
    return f"Translation failed ({type(exc).__name__})"


def _load(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id, populate_existing=True)


def _report(db: Session, job_id: str, progress: ProgressData) -> bool:
    """Persist progress. False means the job row is gone, i.e. it was cancelled."""
    job = _load(db, job_id)
    if job is None:
        return False
    done = min(progress.current, job.cue_count)
    if done != job.processed_cues:
        job.processed_cues = done
        job.step = f"Translating cues {done}/{job.cue_count}"
        db.commit()
    return True


def _to_srt(job: Job, cues: list[Cue]) -> SubRipFile:
    items = [
        SubRipItem(
            index=cue.index,
            start=SubRipTime.from_ordinal(cue.start),
            end=SubRipTime.from_ordinal(cue.end),
            text=cue.source,
        )
        for cue in cues
    ]
    # The path is only used by the library to look up the title for extra LLM context.
    return SubRipFile(items=items, path=job.file_name)


async def run_job(job_id: str) -> None:
    """Translate a job's cues. Idempotent: a job that is gone or finished is skipped."""
    with SessionLocal() as db:
        try:
            job = _load(db, job_id)
            if job is None or job.status != JobStatus.PROCESSING:
                return
            query = select(Cue).where(Cue.job_id == job_id).order_by(Cue.index)
            cues = list(db.scalars(query))
            translator = make_translator()
            progress = ProgressData(total=len(cues), current=0)
            work = asyncio.create_task(
                translate_srt(
                    _to_srt(job, cues),
                    Lang(job.source_lang),
                    Lang(job.target_lang),
                    translator,
                    progress,
                )
            )
            while True:
                done, _ = await asyncio.wait({work}, timeout=_POLL_SECONDS)
                if done:
                    break
                if not _report(db, job_id, progress):
                    work.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await work
                    return
            translated = work.result()
            if _load(db, job_id) is None:
                return
            for cue, item in zip(cues, translated, strict=True):
                cue.target = item.text
            job.processed_cues = job.cue_count
            job.status = JobStatus.READY
            job.step = None
            job.model = translator.model
            db.commit()
        except Exception as exc:
            logger.exception("Translation of job %s failed", job_id)
            db.rollback()
            job = _load(db, job_id)
            if job is not None:
                job.status = JobStatus.FAILED
                job.error = _user_message(exc)
                job.step = None
                db.commit()

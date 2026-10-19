"""Translation business logic: the Celery job body and the inline retranslate.

The heavy lifting is done by `subtaitles`; this module maps jobs/cues to and from it and
reports progress to the database, which is what the UI polls.
"""

import asyncio
import contextlib
import logging
from dataclasses import dataclass
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
    SummaryStatus,
    Usage,
    add_summary,
    get_translated_srt,
    get_translation_request,
)

from app.config import settings
from app.db import SessionLocal
from app.errors import InvalidInputError, UpstreamError
from app.models import AppSettings, Cue, Job, JobStage, JobStatus, UsageKind, User
from app.schemas import CueVariant, JobEstimate
from app.services import app_settings, usage
from app.services.summaries import SummaryStore

logger = logging.getLogger(__name__)

_POLL_SECONDS = 0.5
_CONTEXT_CUES = 2


@cache
def _cache() -> diskcache.Cache | None:
    return diskcache.Cache(settings.srt_cache_dir) if settings.srt_cache_dir else None


def make_translator(config: AppSettings) -> OpenAiTranslator:
    """Build a fresh translator per use: its HTTP client is bound to the running event loop."""
    return OpenAiTranslator(
        model=config.model,
        temperature=app_settings.effective_temperature(config),
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
    translator = make_translator(app_settings.get(db))
    usage.rate_for(db, translator.model)
    try:
        result = asyncio.run(
            translator.retranslate(
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
        # Failed calls may still have consumed tokens; the request rollback must not drop them.
        _record_usage(
            db, job.owner_id, job.id, translator.model, (UsageKind.RETRANSLATE, translator.usage)
        )
        msg = _user_message(exc)
        raise UpstreamError(msg) from exc
    usage.record(
        db,
        user_id=job.owner_id,
        job_id=job.id,
        kind=UsageKind.RETRANSLATE,
        model=result.model or translator.model,
        usage=result.usage,
    )
    return [CueVariant(label=v.label, text=v.text) for v in result.variants]


def _record_usage(
    db: Session, owner_id: int, job_id: str, model: str, *charges: tuple[UsageKind, Usage]
) -> None:
    """Commit what was consumed, also when the job failed or was cancelled."""
    try:
        # The job (or even the user) may be gone by now; the tokens were spent regardless.
        if db.get(User, owner_id) is None:
            return
        for kind, used in charges:
            usage.record(
                db,
                user_id=owner_id,
                job_id=job_id if _load(db, job_id) else None,
                kind=kind,
                model=model,
                usage=used,
            )
        db.commit()
    except Exception:
        logger.exception("Could not record usage of job %s", job_id)
        db.rollback()


def _user_message(exc: Exception) -> str:
    """Short, user-facing reason. Details (which may include key fragments) stay in the log."""
    if isinstance(exc, AuthenticationError):
        return "The translation service is not configured correctly"
    if isinstance(exc, RateLimitError):
        return "The translation service is busy, please try again later"
    if isinstance(exc, InvalidInputError):
        return str(exc)
    return f"Translation failed ({type(exc).__name__})"


def _load(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id, populate_existing=True)


@dataclass
class _Pipeline:
    """Where a running job is, written by the pipeline and persisted by the poll loop."""

    stage: JobStage = JobStage.RECOGNIZING
    summary_status: SummaryStatus | None = None
    # translator usage when translating began: everything before it was the story brief
    translate_baseline: Usage | None = None

    def charges(self, spent: Usage) -> tuple[tuple[UsageKind, Usage], tuple[UsageKind, Usage]]:
        brief = spent if self.translate_baseline is None else self.translate_baseline
        return (UsageKind.SUMMARIZE, brief), (UsageKind.TRANSLATE, spent - brief)


def _report(db: Session, job_id: str, progress: ProgressData, pipeline: _Pipeline) -> bool:
    """Persist progress. False means the job row is gone, i.e. it was cancelled."""
    job = _load(db, job_id)
    if job is None:
        return False
    done = min(progress.current, job.cue_count)
    summary_status = pipeline.summary_status.value if pipeline.summary_status else None
    if (done, pipeline.stage, summary_status) != (
        job.processed_cues,
        job.stage,
        job.summary_status,
    ):
        job.processed_cues = done
        job.stage = pipeline.stage
        job.summary_status = summary_status
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


async def _translate(  # noqa: PLR0913
    srt: SubRipFile,
    source: Lang,
    target: Lang,
    translator: OpenAiTranslator,
    progress: ProgressData,
    pipeline: _Pipeline,
) -> SubRipFile:
    """recognize the title, brief the model on the story, then translate the cues."""
    pipeline.stage = JobStage.RECOGNIZING
    _, request = await get_translation_request(srt, source, target, translator)

    if request.metadata and request.metadata.key:
        pipeline.stage = JobStage.SUMMARIZING
    request, pipeline.summary_status = await add_summary(
        request, translator, SummaryStore(translator.model)
    )

    pipeline.stage = JobStage.TRANSLATING
    pipeline.translate_baseline = translator.usage
    response = await translator.translate(request, progress)
    return get_translated_srt(srt, request, response)


async def run_job(job_id: str) -> None:
    """Translate a job's cues. Idempotent: a job that is gone or finished is skipped."""
    translator: OpenAiTranslator | None = None
    pipeline = _Pipeline()
    with SessionLocal() as db:
        try:
            job = _load(db, job_id)
            if job is None or job.status != JobStatus.PROCESSING:
                return
            owner_id = job.owner_id
            query = select(Cue).where(Cue.job_id == job_id).order_by(Cue.index)
            cues = list(db.scalars(query))
            translator = make_translator(app_settings.get(db))
            usage.rate_for(db, translator.model)
            progress = ProgressData(total=len(cues), current=0)
            work = asyncio.create_task(
                _translate(
                    _to_srt(job, cues),
                    Lang(job.source_lang),
                    Lang(job.target_lang),
                    translator,
                    progress,
                    pipeline,
                )
            )
            while True:
                done, _ = await asyncio.wait({work}, timeout=_POLL_SECONDS)
                if done:
                    break
                if not _report(db, job_id, progress, pipeline):
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
            job.stage = JobStage.TRANSLATING
            job.summary_status = pipeline.summary_status.value if pipeline.summary_status else None
            job.model = translator.model
            db.commit()
        except Exception as exc:
            logger.exception("Translation of job %s failed", job_id)
            db.rollback()
            job = _load(db, job_id)
            if job is not None:
                job.status = JobStatus.FAILED
                job.error = _user_message(exc)
                db.commit()
        finally:
            if translator is not None:
                _record_usage(
                    db, owner_id, job_id, translator.model, *pipeline.charges(translator.usage)
                )

import logging
from datetime import timedelta
from pathlib import PurePath

import srt  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.errors import ConflictError, ErrorCode, InvalidInputError, NotFoundError
from app.models import Cue, Job, JobStatus, User
from app.services import app_settings, languages, usage
from app.worker import translate_job

logger = logging.getLogger(__name__)


def list_for_user(db: Session, user: User, limit: int | None = None) -> list[Job]:
    query = select(Job).where(Job.owner_id == user.id).order_by(Job.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    return list(db.scalars(query))


def get(db: Session, user: User, job_id: str) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.owner_id == user.id))
    if job is None:
        msg = "Job not found"
        raise NotFoundError(ErrorCode.JOB_NOT_FOUND, msg)
    return job


def _parse_srt(file_name: str, content: bytes) -> list[srt.Subtitle]:
    if not file_name.lower().endswith(".srt"):
        msg = "Only .srt files are supported"
        raise InvalidInputError(ErrorCode.FILE_NOT_SRT, msg)
    if len(content) > settings.max_srt_bytes:
        msg = f"File exceeds {settings.max_srt_bytes // (1024 * 1024)}MB"
        raise InvalidInputError(
            ErrorCode.FILE_TOO_LARGE, msg, max_mb=settings.max_srt_bytes // (1024 * 1024)
        )
    try:
        subtitles = list(srt.parse(content.decode("utf-8-sig")))
    except UnicodeDecodeError as exc:
        msg = "File must be UTF-8 encoded"
        raise InvalidInputError(ErrorCode.FILE_NOT_UTF8, msg) from exc
    except srt.SRTParseError as exc:
        msg = "File is not a valid .srt"
        raise InvalidInputError(ErrorCode.FILE_INVALID_SRT, msg) from exc
    if not subtitles:
        msg = "File contains no subtitles"
        raise InvalidInputError(ErrorCode.FILE_EMPTY, msg)
    return subtitles


def _ms(delta: timedelta) -> int:
    return round(delta.total_seconds() * 1000)


def create(  # noqa: PLR0913
    db: Session,
    user: User,
    *,
    file_name: str,
    content: bytes,
    source_lang: str,
    target_lang: str,
) -> Job:
    """Store the job and its cues, and commit so a background worker can see them."""
    if source_lang == target_lang:
        msg = "Source and target language must differ"
        raise InvalidInputError(ErrorCode.SAME_LANGUAGE, msg)
    for code in (source_lang, target_lang):
        if languages.get(db, code) is None:
            msg = f"Unknown language: {code}"
            raise InvalidInputError(ErrorCode.UNKNOWN_LANGUAGE, msg, language=code)
    usage.rate_for(db, app_settings.get(db).model)
    usage.ensure_within_quota(db, user)
    subtitles = _parse_srt(PurePath(file_name).name, content)
    job = Job(
        owner_id=user.id,
        file_name=PurePath(file_name).name,
        source_lang=source_lang,
        target_lang=target_lang,
        cue_count=len(subtitles),
    )
    job.cues = [
        Cue(index=i, start=_ms(sub.start), end=_ms(sub.end), source=sub.content)
        for i, sub in enumerate(subtitles, start=1)
    ]
    db.add(job)
    db.commit()
    return job


def enqueue(db: Session, job: Job) -> None:
    """Hand the job to the Celery worker. Blocking (broker I/O): call off the event loop."""
    try:
        translate_job.delay(job.id)
    except Exception:
        logger.exception("Could not queue job %s", job.id)
        job.status = JobStatus.FAILED
        job.error = ErrorCode.TRANSLATION_QUEUE_FAILED
        db.commit()


def delete(db: Session, user: User, job_id: str) -> None:
    """Also cancels a running translation: the worker stops once its job row is gone."""
    db.delete(get(db, user, job_id))
    db.flush()


def cancel_translation(db: Session, user: User, job_id: str) -> None:
    job = get(db, user, job_id)
    if job.status != JobStatus.PROCESSING:
        msg = "Job is not processing"
        raise ConflictError(ErrorCode.JOB_NOT_PROCESSING, msg)
    delete(db, user, job_id)


def render_srt(db: Session, user: User, job_id: str) -> tuple[str, str]:
    """Return (download file name, .srt text) built from the translated cues."""
    job = get(db, user, job_id)
    if job.status != JobStatus.READY:
        msg = "Translation is not ready"
        raise ConflictError(ErrorCode.TRANSLATION_NOT_READY, msg)
    subtitles = [
        srt.Subtitle(
            index=cue.index,
            start=timedelta(milliseconds=cue.start),
            end=timedelta(milliseconds=cue.end),
            content=cue.target,
        )
        for cue in job.cues
    ]
    stem = PurePath(job.file_name).stem
    return f"{stem}.{job.target_lang}.srt", srt.compose(subtitles)

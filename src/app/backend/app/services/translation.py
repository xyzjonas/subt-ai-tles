"""PLACEHOLDER business logic.

Everything here fakes the real pipeline (`subtaitles.translate_srt`) behind the interface the
rest of the app uses. Swapping in the real implementation should only touch this module.
"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Cue, Job, JobStatus
from app.schemas import CueVariant, JobEstimate

logger = logging.getLogger(__name__)

_COMMIT_EVERY = 10
_CUE_DELAY_SECONDS = 0.02
_tasks: set[asyncio.Task[None]] = set()


def estimate(cue_count: int) -> JobEstimate:
    return JobEstimate(seconds=max(5, round(cue_count / 24)), tokens=cue_count * 5)


def detect_language(content: bytes) -> str:  # noqa: ARG001
    return "en"


def retranslate_cue(cue: Cue, prompt: str | None) -> list[CueVariant]:
    if prompt:
        return [CueVariant(label="Custom", text=f"[custom] {cue.source}")]
    return [
        CueVariant(label="Literal", text=f"[literal] {cue.source}"),
        CueVariant(label="Punchy / Action", text=f"[punchy] {cue.source}"),
        CueVariant(label="Shorter", text=f"[shorter] {cue.source}"),
    ]


def start_job(job_id: str) -> None:
    """Schedules the fake translation. Must be called from the running event loop."""
    task = asyncio.create_task(_run(job_id))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


def recover_interrupted(db: Session) -> None:
    """Jobs still processing at startup lost their worker with the previous process."""
    for job in db.scalars(select(Job).where(Job.status == JobStatus.PROCESSING)):
        job.status = JobStatus.FAILED
        job.error = "Interrupted by server restart"
        job.step = None
    db.commit()


def _load(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id, populate_existing=True)


async def _run(job_id: str) -> None:
    with SessionLocal() as db:
        try:
            job = _load(db, job_id)
            if job is None:
                return
            query = select(Cue).where(Cue.job_id == job_id).order_by(Cue.index)
            cues = list(db.scalars(query))
            for done, cue in enumerate(cues, start=1):
                await asyncio.sleep(_CUE_DELAY_SECONDS)
                cue.target = f"[stub] {cue.source}"
                if done % _COMMIT_EVERY and done != len(cues):
                    continue
                job.processed_cues = done
                job.step = f"Translating cues {done}/{len(cues)}"
                db.commit()
                # The job row disappearing is how cancellation reaches the worker.
                if _load(db, job_id) is None:
                    return
            job.status = JobStatus.READY
            job.step = None
            job.model = "placeholder"
            job.confidence = 99.0
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.warning("Translation of job %s stopped: %s", job_id, exc)
            job = _load(db, job_id)
            if job is not None:
                job.status = JobStatus.FAILED
                job.error = str(exc)
                job.step = None
                db.commit()

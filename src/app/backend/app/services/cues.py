from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models import Cue, User
from app.schemas import CueUpdate, CueVariant
from app.services import jobs, translation


def list_for_job(db: Session, user: User, job_id: str) -> list[Cue]:
    jobs.get(db, user, job_id)
    return list(db.scalars(select(Cue).where(Cue.job_id == job_id).order_by(Cue.index)))


def get(db: Session, user: User, job_id: str, index: int) -> Cue:
    jobs.get(db, user, job_id)
    cue = db.scalar(select(Cue).where(Cue.job_id == job_id, Cue.index == index))
    if cue is None:
        msg = "Cue not found"
        raise NotFoundError(msg)
    return cue


def update_target(db: Session, user: User, job_id: str, index: int, data: CueUpdate) -> Cue:
    cue = get(db, user, job_id, index)
    cue.target = data.target
    db.flush()
    return cue


def retranslate(
    db: Session, user: User, job_id: str, index: int, prompt: str | None
) -> list[CueVariant]:
    cue = get(db, user, job_id, index)
    return translation.retranslate_cue(cue, prompt)

from fastapi import APIRouter

from app.db import DbDep
from app.schemas import CueOut, CueUpdate, CueVariant, RetranslateRequest
from app.security import CurrentUser
from app.services import cues

router = APIRouter(prefix="/jobs/{job_id}/cues", tags=["cues"])


@router.get("")
def list_cues(job_id: str, db: DbDep, user: CurrentUser) -> list[CueOut]:
    return [CueOut.model_validate(cue) for cue in cues.list_for_job(db, user, job_id)]


@router.get("/{index}")
def get_cue(job_id: str, index: int, db: DbDep, user: CurrentUser) -> CueOut:
    return CueOut.model_validate(cues.get(db, user, job_id, index))


@router.patch("/{index}")
def update_cue(
    job_id: str, index: int, body: CueUpdate, db: DbDep, user: CurrentUser
) -> CueOut:
    return CueOut.model_validate(cues.update_target(db, user, job_id, index, body))


@router.post("/{index}/retranslate")
def retranslate_cue(
    job_id: str, index: int, body: RetranslateRequest, db: DbDep, user: CurrentUser
) -> list[CueVariant]:
    return cues.retranslate(db, user, job_id, index, body.prompt)

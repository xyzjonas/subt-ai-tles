from typing import Annotated

from fastapi import APIRouter, Form, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.db import DbDep
from app.schemas import JobEstimate, JobOut
from app.schemas.job import EstimateRequest
from app.security import CurrentUser
from app.services import jobs, translation

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model_exclude_none=True)
def list_jobs(db: DbDep, user: CurrentUser, limit: int | None = None) -> list[JobOut]:
    return [JobOut.model_validate(job) for job in jobs.list_for_user(db, user, limit)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
async def create_job(
    db: DbDep,
    user: CurrentUser,
    file: UploadFile,
    source_lang: Annotated[str, Form(alias="sourceLang")],
    target_lang: Annotated[str, Form(alias="targetLang")],
) -> JobOut:
    content = await file.read(settings.max_srt_bytes + 1)
    job = jobs.create(
        db,
        user,
        file_name=file.filename or "subtitles.srt",
        content=content,
        source_lang=source_lang,
        target_lang=target_lang,
    )
    await run_in_threadpool(jobs.enqueue, db, job)
    return JobOut.model_validate(job)


@router.post("/estimate")
def estimate_job(body: EstimateRequest, _user: CurrentUser) -> JobEstimate:
    return translation.estimate(body.cue_count)


@router.get("/{job_id}", response_model_exclude_none=True)
def get_job(job_id: str, db: DbDep, user: CurrentUser) -> JobOut:
    return JobOut.model_validate(jobs.get(db, user, job_id))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: DbDep, user: CurrentUser) -> None:
    jobs.delete(db, user, job_id)


@router.delete("/{job_id}/translation", status_code=status.HTTP_204_NO_CONTENT)
def cancel_translation(job_id: str, db: DbDep, user: CurrentUser) -> None:
    jobs.cancel_translation(db, user, job_id)


@router.get("/{job_id}/download")
def download_job(job_id: str, db: DbDep, user: CurrentUser) -> Response:
    file_name, text = jobs.render_srt(db, user, job_id)
    return Response(
        content=text,
        media_type="application/x-subrip",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )

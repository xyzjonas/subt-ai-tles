from datetime import datetime

from pydantic import Field

from app.models.job import JobStage, JobStatus
from app.schemas.base import CamelModel


class JobOut(CamelModel):
    id: str
    file_name: str
    source_lang: str | None = None
    target_lang: str
    cue_count: int
    created_at: datetime
    folder_id: str | None = None
    archived_at: datetime | None = None
    status: JobStatus
    processed_cues: int | None = None
    stage: JobStage | None = None
    summary_status: str | None = None
    model: str | None = None
    confidence: float | None = None
    error: str | None = None


class EstimateRequest(CamelModel):
    cue_count: int = Field(ge=0)


class JobEstimate(CamelModel):
    seconds: int
    tokens: int


class JobUpdate(CamelModel):
    """Only the fields present are changed; `folderId: null` takes the job out of its folder."""

    folder_id: str | None = None
    archived: bool | None = None

from datetime import datetime

from pydantic import Field

from app.models.job import JobStatus
from app.schemas.base import CamelModel


class JobOut(CamelModel):
    id: str
    file_name: str
    source_lang: str
    target_lang: str
    cue_count: int
    created_at: datetime
    status: JobStatus
    processed_cues: int | None = None
    step: str | None = None
    model: str | None = None
    confidence: float | None = None
    error: str | None = None


class EstimateRequest(CamelModel):
    cue_count: int = Field(ge=0)


class JobEstimate(CamelModel):
    seconds: int
    tokens: int

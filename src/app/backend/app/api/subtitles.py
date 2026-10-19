from fastapi import APIRouter, Depends, UploadFile

from app.config import settings
from app.schemas import DetectedLanguage
from app.security import current_user
from app.services import translation

router = APIRouter(
    prefix="/subtitles", tags=["subtitles"], dependencies=[Depends(current_user)]
)


@router.post("/detect-language")
async def detect_language(file: UploadFile) -> DetectedLanguage:
    content = await file.read(settings.max_srt_bytes + 1)
    return DetectedLanguage(code=translation.detect_language(content))

from fastapi import APIRouter, Depends

from app.db import DbDep
from app.schemas import LanguageOut
from app.security import current_user
from app.services import languages

router = APIRouter(tags=["languages"], dependencies=[Depends(current_user)])


@router.get("/languages", response_model_exclude_none=True)
def list_languages(db: DbDep) -> list[LanguageOut]:
    return [LanguageOut.model_validate(lang) for lang in languages.list_all(db)]

from fastapi import APIRouter, Depends

from app.db import DbDep
from app.schemas import AppSettingsIn, AppSettingsOut
from app.security import require_admin
from app.services import app_settings

router = APIRouter(
    prefix="/admin/settings", tags=["admin"], dependencies=[Depends(require_admin)]
)


@router.get("")
def get_settings(db: DbDep) -> AppSettingsOut:
    return app_settings.view(db)


@router.put("")
def update_settings(body: AppSettingsIn, db: DbDep) -> AppSettingsOut:
    app_settings.update(db, body)
    return app_settings.view(db)

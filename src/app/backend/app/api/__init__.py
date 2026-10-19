from fastapi import APIRouter

from app.api import (
    admin_rates,
    admin_settings,
    admin_users,
    auth,
    cues,
    jobs,
    languages,
    subtitles,
    usage,
)

api_router = APIRouter(prefix="/api")
for _module in (
    auth,
    languages,
    jobs,
    cues,
    subtitles,
    usage,
    admin_users,
    admin_rates,
    admin_settings,
):
    api_router.include_router(_module.router)

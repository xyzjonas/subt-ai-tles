from fastapi import APIRouter

from app.api import (
    admin_rates,
    admin_settings,
    admin_users,
    auth,
    cues,
    folders,
    jobs,
    languages,
    membership_requests,
    usage,
)

api_router = APIRouter(prefix="/api")
for _module in (
    auth,
    languages,
    jobs,
    folders,
    cues,
    usage,
    admin_users,
    admin_rates,
    admin_settings,
    membership_requests,
):
    api_router.include_router(_module.router)

from fastapi import APIRouter

from app.api import admin_users, auth, cues, jobs, languages, subtitles

api_router = APIRouter(prefix="/api")
for _module in (auth, languages, jobs, cues, subtitles, admin_users):
    api_router.include_router(_module.router)

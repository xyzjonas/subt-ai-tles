from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api import api_router
from app.db import DbSessionMiddleware, SessionLocal
from app.errors import ConflictError, InvalidInputError, NotFoundError, ServiceError
from app.services import languages, translation, users

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    InvalidInputError: 422,
}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Schema is managed by Alembic (`just db-upgrade`, run by docker-entrypoint.sh).
    with SessionLocal() as db:
        languages.seed(db)
        users.ensure_bootstrap_admin(db)
        translation.recover_interrupted(db)
    yield


async def _service_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse({"detail": str(exc)}, status_code=code)


def create_app() -> FastAPI:
    app = FastAPI(title="subt-ai-tles", lifespan=lifespan)
    app.add_middleware(DbSessionMiddleware)
    app.add_exception_handler(ServiceError, _service_error_handler)
    app.include_router(api_router)
    return app


app = create_app()

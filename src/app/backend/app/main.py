from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api import api_router
from app.db import DbSessionMiddleware, SessionLocal
from app.errors import (
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    QuotaExceededError,
    ServiceError,
    UnauthorizedError,
    UpstreamError,
)
from app.services import languages, users

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    InvalidInputError: 422,
    QuotaExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    UpstreamError: status.HTTP_502_BAD_GATEWAY,
}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Schema is managed by Alembic (`just db-upgrade`, run by docker-entrypoint.sh).
    with SessionLocal() as db:
        languages.seed(db)
        users.ensure_bootstrap_admin(db)
    yield


async def _service_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ServiceError)
    http_status = _STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    body = {"detail": str(exc), "code": exc.code, "params": exc.params}
    return JSONResponse(body, status_code=http_status)


def create_app() -> FastAPI:
    app = FastAPI(title="subt-ai-tles", lifespan=lifespan)
    app.add_middleware(DbSessionMiddleware)
    app.add_exception_handler(ServiceError, _service_error_handler)
    app.include_router(api_router)
    return app


app = create_app()

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request, Response
from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.engine import Dialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry
from sqlalchemy.types import TypeDecorator
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(
        dbapi_connection: DBAPIConnection, _record: ConnectionPoolEntry
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # The web and worker processes share the file: readers must not block the writer.
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class UtcDateTime(TypeDecorator[datetime]):
    """Stores UTC; SQLite drops tzinfo so it is re-attached on read."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self,
        value: datetime | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> datetime | None:
        return None if value is None else value.astimezone(UTC)

    def process_result_value(
        self,
        value: datetime | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> datetime | None:
        return None if value is None else value.replace(tzinfo=UTC)


class DbSessionMiddleware(BaseHTTPMiddleware):
    """Opens one session per request; commits on success, rolls back on error responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        db = SessionLocal()
        request.state.db = db
        try:
            response = await call_next(request)
        except BaseException:
            db.rollback()
            raise
        else:
            if response.status_code < 400:  # noqa: PLR2004
                db.commit()
            else:
                db.rollback()
            return response
        finally:
            db.close()


def get_db(request: Request) -> Session:
    return request.state.db  # type: ignore[no-any-return]


DbDep = Annotated[Session, Depends(get_db)]

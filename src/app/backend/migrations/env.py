from logging.config import fileConfig
from typing import Any

from alembic import context
from app.config import settings
from app.db import Base, UtcDateTime, engine

from app import models  # noqa: F401  (registers tables on Base.metadata)

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def _render_item(type_: str, obj: Any, _autogen_context: Any) -> str | bool:  # noqa: ANN401
    # Keep migrations independent of app code: render the custom type as its plain impl.
    if type_ == "type" and isinstance(obj, UtcDateTime):
        return "sa.DateTime(timezone=True)"
    return False


def _configure(**kwargs: Any) -> None:  # noqa: ANN401
    context.configure(
        target_metadata=Base.metadata,
        render_item=_render_item,
        render_as_batch=settings.database_url.startswith("sqlite"),  # SQLite lacks ALTER
        **kwargs,
    )


def run_migrations_offline() -> None:
    _configure(url=settings.database_url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        _configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

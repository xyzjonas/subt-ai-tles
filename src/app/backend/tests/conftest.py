import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

# Must be set before `app` is imported: engine/settings are created at import time.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp) / 'test.db'}"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin-password"

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

ALEMBIC_CFG = Config(str(Path(__file__).parents[1] / "alembic.ini"))
# The test schema comes from the real migrations.
command.upgrade(ALEMBIC_CFG, "head")

ADMIN = ("admin", "admin-password")

SRT = (
    "1\n00:00:01,000 --> 00:00:02,500\nHello there\n\n"
    "2\n00:00:03,000 --> 00:00:04,000\nGeneral Kenobi\n"
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_user(client: TestClient):
    def _make(username: str, *, admin: bool = False) -> tuple[str, str]:
        r = client.post(
            "/api/admin/users",
            json={"username": username, "password": "password123", "isAdmin": admin},
            auth=ADMIN,
        )
        assert r.status_code in (201, 409), r.text
        return username, "password123"

    return _make

import asyncio
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
from app.services import app_settings, jobs, translation  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from subtaitles import (  # noqa: E402
    RetranslationResponse,
    TranslatedSegment,
    TranslationResponse,
    TranslationVariant,
    Usage,
)

ALEMBIC_CFG = Config(str(Path(__file__).parents[1] / "alembic.ini"))
# The test schema comes from the real migrations.
command.upgrade(ALEMBIC_CFG, "head")

# 400 prompt + 100 completion tokens per story brief: 0.4 + 0.4 = 0.8 credits
SUMMARY_USAGE = Usage(400, 100)

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
            json={"username": username, "password": "temporary-1", "isAdmin": admin},
            auth=ADMIN,
        )
        assert r.status_code in (201, 409), r.text
        if r.status_code == 201:
            # First login: replace the temporary password.
            changed = client.post(
                "/api/auth/password",
                json={"currentPassword": "temporary-1", "newPassword": "password123"},
                auth=(username, "temporary-1"),
            )
            assert changed.status_code == 204, changed.text
        return username, "password123"

    return _make


class StubTranslator:
    """Stands in for OpenAiTranslator: no network, deterministic output."""

    model = "gpt-4.1-nano"
    temperature: float | None = 0.0

    def __init__(self) -> None:
        self.usage = Usage()
        self.fail_after_usage = False
        self.summarized: list[str | None] = []

    async def summarize(self, request):
        self.summarized.append(request.metadata.key if request.metadata else None)
        self.usage += SUMMARY_USAGE
        return f"brief of {request.metadata.title}"

    async def translate(self, request, progress=None):
        segments = []
        for seg in request.segments:
            segments.append(
                TranslatedSegment(seg.index, seg.text, f"[stub] {seg.text}", "translated")
            )
            if progress:
                progress.current += 1
        # 1,000 prompt + 500 completion tokens per cue: 1 + 2 = 3 credits at the seeded rates
        used = Usage(1000 * len(segments), 500 * len(segments))
        self.usage += used
        if self.fail_after_usage:
            msg = "boom"
            raise RuntimeError(msg)
        return TranslationResponse(
            tuple(segments), request.source, request.target, usage=used, model=self.model
        )

    async def retranslate(self, text, *, prompt=None, **_kwargs):
        used = Usage(1000, 500)
        self.usage += used
        if prompt:
            variants = [TranslationVariant("Custom", f"[custom] {text}")]
        else:
            variants = [
                TranslationVariant(label, f"[{label}] {text}")
                for label in ("Literal", "Shorter")
            ]
        return RetranslationResponse(variants, used, self.model)


class FakeQueue:
    """Replaces the Celery task: jobs are recorded and only run when a test says so."""

    def __init__(self) -> None:
        self.job_ids: list[str] = []
        self.fail = False

    def delay(self, job_id: str) -> None:
        if self.fail:
            msg = "broker down"
            raise ConnectionError(msg)
        self.job_ids.append(job_id)

    def run_all(self) -> None:
        for job_id in self.job_ids:
            asyncio.run(translation.run_job(job_id))


@pytest.fixture(autouse=True)
def translator(monkeypatch: pytest.MonkeyPatch) -> StubTranslator:
    stub = StubTranslator()

    def build(config, cache):
        # what the real make_translator takes from the app settings
        stub.usage = Usage()  # the real translator is fresh per use
        stub.model = config.model
        stub.temperature = app_settings.effective_temperature(config)
        return stub

    monkeypatch.setattr(translation, "make_translator", build)

    async def no_lookup(_path: str) -> None:
        msg = "offline"
        raise RuntimeError(msg)

    monkeypatch.setattr("mediasorter.whats_this", no_lookup)
    return stub


@pytest.fixture(autouse=True)
def queue(monkeypatch: pytest.MonkeyPatch) -> FakeQueue:
    fake = FakeQueue()
    monkeypatch.setattr(jobs, "translate_job", fake)
    return fake

import asyncio
from collections.abc import Callable

import pytest
from app.db import SessionLocal
from app.models import Job, JobStage, StorySummary
from app.services import translation
from app.services.summaries import SummaryStore
from fastapi.testclient import TestClient
from mediasorter import TvShowMetadata
from sqlalchemy import delete

from tests.conftest import SUMMARY_USAGE, FakeQueue, StubTranslator
from tests.test_api import _finish, _upload

KEY = "tv:the-office:s02e05"


@pytest.fixture(autouse=True)
def no_stored_briefs() -> None:
    with SessionLocal() as db:
        db.execute(delete(StorySummary))
        db.commit()


@pytest.fixture
def recognized(monkeypatch: pytest.MonkeyPatch) -> None:
    async def lookup(_path: str, **_kwargs: object) -> TvShowMetadata:
        return TvShowMetadata(
            series_title="The Office",
            season_id=2,
            episode_id=5,
            episode_title="Halloween",
            episode_summary="Michael fires someone.",
        )

    monkeypatch.setattr("mediasorter.whats_this", lookup)


def _stored(key: str) -> StorySummary | None:
    with SessionLocal() as db:
        return db.get(StorySummary, key)


def test_summary_is_made_once_per_recognized_title(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
    recognized: None,  # noqa: ARG001
) -> None:
    sumner = make_user("sumner")

    _finish(client, queue, sumner, _upload(client, sumner)["id"])
    assert translator.summarized == [KEY]
    row = _stored(KEY)
    assert row is not None
    assert row.summary == "brief of The Office"
    assert row.model == translator.model

    queue.job_ids.clear()
    _finish(client, queue, sumner, _upload(client, sumner)["id"])
    assert translator.summarized == [KEY]  # second job reused the stored brief


def test_unrecognized_media_is_not_summarized(
    client: TestClient, make_user: Callable, queue: FakeQueue, translator: StubTranslator
) -> None:
    sumpter = make_user("sumpter")

    _finish(client, queue, sumpter, _upload(client, sumpter)["id"])

    assert translator.summarized == []


def test_store_put_keeps_first_summary() -> None:
    store = SummaryStore("gpt-4.1-nano")

    async def run() -> str | None:
        await store.put("movie:dune:2021", "first")
        await store.put("movie:dune:2021", "second")
        return await store.get("movie:dune:2021")

    assert asyncio.run(run()) == "first"
    assert asyncio.run(store.get("movie:missing:1999")) is None


def _kinds(client: TestClient, auth: tuple[str, str]) -> dict[str, dict]:
    records = client.get("/api/usage/records", auth=auth).json()
    return {r["kind"]: r for r in records}


def test_summary_has_its_own_usage_row(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    recognized: None,  # noqa: ARG001
) -> None:
    sally = make_user("sally")

    job = _finish(client, queue, sally, _upload(client, sally)["id"])

    rows = _kinds(client, sally)
    assert rows["summarize"]["promptTokens"] == SUMMARY_USAGE.prompt_tokens
    assert rows["summarize"]["completionTokens"] == SUMMARY_USAGE.completion_tokens
    assert rows["summarize"]["credits"] == pytest.approx(0.8)
    assert rows["summarize"]["jobId"] == job["id"]
    # the translation row doesn't include the brief
    assert rows["translate"]["promptTokens"] == 2000
    assert rows["translate"]["completionTokens"] == 1000
    assert job["summaryStatus"] == "generated"


def test_stored_brief_costs_nothing(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    recognized: None,  # noqa: ARG001
) -> None:
    sam = make_user("sam")
    _finish(client, queue, sam, _upload(client, sam)["id"])
    queue.job_ids.clear()

    job = _finish(client, queue, sam, _upload(client, sam)["id"])

    assert job["summaryStatus"] == "stored"
    records = client.get("/api/usage/records", auth=sam).json()
    assert [r["kind"] for r in records].count("summarize") == 1  # only the first job's


def test_unrecognized_media_has_no_summary_row(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    sid = make_user("sid")

    job = _finish(client, queue, sid, _upload(client, sid)["id"])

    assert job["summaryStatus"] == "skipped"
    assert set(_kinds(client, sid)) == {"translate"}


def test_failed_brief_is_billed_and_translation_continues(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
    recognized: None,  # noqa: ARG001
) -> None:
    stu = make_user("stu")
    job = _upload(client, stu)

    async def spend_then_fail(_request):
        translator.usage += SUMMARY_USAGE
        msg = "boom"
        raise RuntimeError(msg)

    translator.summarize = spend_then_fail  # type: ignore[method-assign]

    done = _finish(client, queue, stu, job["id"])

    assert done["status"] == "ready"
    assert done["summaryStatus"] == "failed"
    rows = _kinds(client, stu)
    assert rows["summarize"]["promptTokens"] == SUMMARY_USAGE.prompt_tokens
    assert rows["translate"]["promptTokens"] == 2000


def test_cancel_while_summarizing_bills_the_brief(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
    monkeypatch: pytest.MonkeyPatch,
    recognized: None,  # noqa: ARG001
) -> None:
    monkeypatch.setattr(translation, "_POLL_SECONDS", 0.01)
    sven = make_user("sven")
    job = _upload(client, sven)
    stages: list[JobStage] = []

    async def hang(_request):
        translator.usage += SUMMARY_USAGE
        with SessionLocal() as db:
            await asyncio.sleep(0.05)  # let the poll loop persist the stage
            row = db.get(Job, job["id"], populate_existing=True)
            stages.append(row.stage)
            db.delete(row)  # the user cancels
            db.commit()
        await asyncio.sleep(10)

    translator.summarize = hang  # type: ignore[method-assign]

    queue.run_all()

    assert stages == [JobStage.SUMMARIZING]
    assert set(_kinds(client, sven)) == {"summarize"}

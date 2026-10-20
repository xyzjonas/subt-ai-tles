from collections.abc import Callable

from app.db import SessionLocal
from app.models import AppSettings, Job
from fastapi.testclient import TestClient

from tests.conftest import ADMIN, FakeQueue, StubTranslator
from tests.test_api import _finish, _upload

JOB_CREDITS = 6.0  # two cues, 3 credits each
RETRANSLATE_CREDITS = 3.0


def _user_id(client: TestClient, username: str) -> int:
    users = client.get("/api/admin/users", auth=ADMIN).json()
    return next(u["id"] for u in users if u["username"] == username)


def _records(client: TestClient, auth: tuple[str, str]) -> list[dict]:
    return client.get("/api/usage/records", auth=auth).json()


def test_translation_is_recorded(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    ann = make_user("ann")
    job = _upload(client, ann)
    assert _records(client, ann) == []

    _finish(client, queue, ann, job["id"])

    (record,) = _records(client, ann)
    assert record["kind"] == "translate"
    assert record["model"] == "gpt-4.1-nano"
    assert record["jobId"] == job["id"]
    assert record["promptTokens"] == 2000
    assert record["completionTokens"] == 1000
    assert record["totalTokens"] == 3000
    assert record["credits"] == JOB_CREDITS


def test_retranslate_is_recorded(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    ben = make_user("ben")
    job = _upload(client, ben)
    _finish(client, queue, ben, job["id"])

    r = client.post(f"/api/jobs/{job['id']}/cues/1/retranslate", json={}, auth=ben)

    assert r.status_code == 200
    kinds = [rec["kind"] for rec in _records(client, ben)]
    assert kinds == ["retranslate", "translate"]  # newest first
    assert _records(client, ben)[0]["credits"] == RETRANSLATE_CREDITS


def test_failed_job_still_records_spent_tokens(
    client: TestClient, make_user: Callable, queue: FakeQueue, translator: StubTranslator
) -> None:
    cy = make_user("cy")
    job = _upload(client, cy)
    translator.fail_after_usage = True

    assert _finish(client, queue, cy, job["id"])["status"] == "failed"

    (record,) = _records(client, cy)
    assert record["credits"] == JOB_CREDITS


def test_usage_survives_cancelled_job(
    client: TestClient, make_user: Callable, queue: FakeQueue, translator: StubTranslator
) -> None:
    dee = make_user("dee")
    job = _upload(client, dee)
    translator.fail_after_usage = True
    with SessionLocal() as db:
        # simulates the job row disappearing while the worker was busy
        db.delete(db.get(Job, job["id"]))
        db.commit()

    queue.run_all()  # job is gone: nothing to translate, nothing to record
    assert _records(client, dee) == []

    job = _upload(client, dee)
    translator.fail_after_usage = False
    _finish(client, queue, dee, job["id"])
    client.delete(f"/api/jobs/{job['id']}", auth=dee)

    (record,) = _records(client, dee)
    assert record["jobId"] is None
    assert record["credits"] == JOB_CREDITS


def test_usage_is_private_to_each_user(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    eve, fay = make_user("eve"), make_user("fay")
    _finish(client, queue, eve, _upload(client, eve)["id"])

    assert len(_records(client, eve)) == 1
    assert _records(client, fay) == []
    assert client.get("/api/usage", auth=fay).json()["quota"]["used"] == 0


def test_summary_and_quota(client: TestClient, make_user: Callable, queue: FakeQueue) -> None:
    gus = make_user("gus")
    _finish(client, queue, gus, _upload(client, gus)["id"])

    summary = client.get("/api/usage", auth=gus).json()

    assert summary["quota"] == {
        "limit": 1000,
        "used": JOB_CREDITS,
        "remaining": 1000 - JOB_CREDITS,
    }
    assert (len(summary["daily"]), len(summary["weekly"]), len(summary["monthly"])) == (
        30,
        12,
        12,
    )
    for buckets in (summary["daily"], summary["weekly"], summary["monthly"]):
        last = buckets[-1]  # the current period
        assert (last["requests"], last["tokens"], last["credits"]) == (1, 3000, JOB_CREDITS)
        assert sum(b["requests"] for b in buckets) == 1


def test_quota_blocks_new_work(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    hal = make_user("hal")
    job = _upload(client, hal)
    _finish(client, queue, hal, job["id"])
    r = client.patch(
        f"/api/admin/users/{_user_id(client, 'hal')}", json={"monthlyQuota": 5}, auth=ADMIN
    )
    assert r.json()["monthlyQuota"] == 5

    upload = client.post(
        "/api/jobs",
        files={"file": ("movie.srt", b"1\n00:00:01,000 --> 00:00:02,000\nHi\n", "text/plain")},
        data={"targetLang": "de"},
        auth=hal,
    )
    retranslate = client.post(f"/api/jobs/{job['id']}/cues/1/retranslate", json={}, auth=hal)

    assert upload.status_code == 429
    assert retranslate.status_code == 429
    assert upload.json()["code"] == "quota_exceeded"
    assert client.get("/api/usage", auth=hal).json()["quota"]["remaining"] == 0


def test_unlisted_model_is_rejected(client: TestClient, make_user: Callable) -> None:
    ivy = make_user("ivy")
    with SessionLocal() as db:
        db.get(AppSettings, 1).model = "gpt-unlisted"
        db.commit()

    try:
        r = client.post(
            "/api/jobs",
            files={
                "file": ("movie.srt", b"1\n00:00:01,000 --> 00:00:02,000\nHi\n", "text/plain")
            },
            data={"targetLang": "de"},
            auth=ivy,
        )
    finally:
        with SessionLocal() as db:
            db.get(AppSettings, 1).model = "gpt-4.1-nano"
            db.commit()

    assert r.status_code == 422


def test_model_rates_are_admin_configurable(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    jo = make_user("jo")
    assert client.get("/api/admin/model-rates", auth=jo).status_code == 403
    assert client.put("/api/admin/model-rates/x", json={}, auth=jo).status_code == 403

    rates = client.get("/api/admin/model-rates", auth=ADMIN).json()
    assert {
        "model": "gpt-4.1-nano",
        "inputCreditsPer1K": 1.0,
        "outputCreditsPer1K": 4.0,
    } in rates

    _finish(client, queue, jo, _upload(client, jo)["id"])
    client.put(
        "/api/admin/model-rates/gpt-4.1-nano",
        json={"inputCreditsPer1K": 2.0, "outputCreditsPer1K": 8.0},
        auth=ADMIN,
    )
    _finish(client, queue, jo, _upload(client, jo)["id"])

    newest, oldest = _records(client, jo)
    assert newest["credits"] == JOB_CREDITS * 2
    assert oldest["credits"] == JOB_CREDITS  # history is not rewritten
    client.put(
        "/api/admin/model-rates/gpt-4.1-nano",
        json={"inputCreditsPer1K": 1.0, "outputCreditsPer1K": 4.0},
        auth=ADMIN,
    )

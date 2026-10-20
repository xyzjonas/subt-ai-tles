import asyncio
from collections.abc import Callable

import pytest
from app.db import SessionLocal
from app.models import Job, JobStage
from app.services import translation
from fastapi.testclient import TestClient

from tests.conftest import ADMIN, SRT, FakeQueue, StubTranslator


def _upload(client: TestClient, auth: tuple[str, str], body: bytes = SRT.encode()) -> dict:
    r = client.post(
        "/api/jobs",
        files={"file": ("movie.srt", body, "application/x-subrip")},
        data={"sourceLang": "en", "targetLang": "de"},
        auth=auth,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _finish(client: TestClient, queue: FakeQueue, auth: tuple[str, str], job_id: str) -> dict:
    queue.run_all()
    return client.get(f"/api/jobs/{job_id}", auth=auth).json()


def test_auth(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", auth=("admin", "nope")).status_code == 401
    me = client.get("/api/auth/me", auth=ADMIN).json()
    assert me["username"] == "admin"
    assert me["isAdmin"] is True


def test_languages(client: TestClient) -> None:
    langs = client.get("/api/languages", auth=ADMIN).json()
    assert len(langs) > 50
    assert {"code": "en", "name": "English", "flag": "🇬🇧"} in langs


def test_admin_user_crud(client: TestClient, make_user: Callable) -> None:
    alice = make_user("alice")
    assert client.get("/api/admin/users", auth=alice).status_code == 403

    users = client.get("/api/admin/users", auth=ADMIN).json()
    alice_id = next(u["id"] for u in users if u["username"] == "alice")
    assert (
        client.post(
            "/api/admin/users",
            json={"username": "alice", "password": "password123"},
            auth=ADMIN,
        ).status_code
        == 409
    )
    r = client.patch(f"/api/admin/users/{alice_id}", json={"isActive": False}, auth=ADMIN)
    assert r.json()["isActive"] is False
    assert client.get("/api/auth/me", auth=alice).status_code == 401
    assert client.delete(f"/api/admin/users/{alice_id}", auth=ADMIN).status_code == 204
    assert client.get(f"/api/admin/users/{alice_id}", auth=ADMIN).status_code == 404


def test_last_admin_guards(client: TestClient) -> None:
    admin_id = client.get("/api/auth/me", auth=ADMIN).json()["id"]
    assert client.delete(f"/api/admin/users/{admin_id}", auth=ADMIN).status_code == 409
    r = client.patch(f"/api/admin/users/{admin_id}", json={"isAdmin": False}, auth=ADMIN)
    assert r.status_code == 409
    assert client.get("/api/auth/me", auth=ADMIN).json()["isAdmin"] is True


def test_job_lifecycle(client: TestClient, make_user: Callable, queue: FakeQueue) -> None:
    bob = make_user("bob")
    job = _upload(client, bob)
    assert job["status"] == "processing"
    assert job["cueCount"] == 2
    assert queue.job_ids == [job["id"]]

    done = _finish(client, queue, bob, job["id"])
    assert done["status"] == "ready"
    assert done["processedCues"] == 2
    assert done["model"] == "gpt-4.1-nano"

    cues = client.get(f"/api/jobs/{job['id']}/cues", auth=bob).json()
    assert cues[0] == {
        "index": 1,
        "start": 1000,
        "end": 2500,
        "source": "Hello there",
        "target": "[stub] Hello there",
    }

    r = client.patch(f"/api/jobs/{job['id']}/cues/2", json={"target": "Hallo"}, auth=bob)
    assert r.json()["target"] == "Hallo"

    variants = client.post(
        f"/api/jobs/{job['id']}/cues/1/retranslate", json={}, auth=bob
    ).json()
    assert [v["label"] for v in variants] == ["Literal", "Shorter"]
    custom = client.post(
        f"/api/jobs/{job['id']}/cues/1/retranslate", json={"prompt": "pirate"}, auth=bob
    ).json()
    assert [v["label"] for v in custom] == ["Custom"]

    dl = client.get(f"/api/jobs/{job['id']}/download", auth=bob)
    assert dl.headers["content-disposition"] == 'attachment; filename="movie.de.srt"'
    assert "Hallo" in dl.text

    assert client.get("/api/jobs", auth=bob).json()[0]["id"] == job["id"]
    assert client.delete(f"/api/jobs/{job['id']}", auth=bob).status_code == 204
    assert client.get(f"/api/jobs/{job['id']}", auth=bob).status_code == 404


def test_cancel_translation(client: TestClient, make_user: Callable, queue: FakeQueue) -> None:
    carol = make_user("carol")
    job = _upload(client, carol)
    assert client.delete(f"/api/jobs/{job['id']}/translation", auth=carol).status_code == 204
    assert client.get(f"/api/jobs/{job['id']}", auth=carol).status_code == 404
    queue.run_all()  # the worker picks up a cancelled job and skips it


def test_cancel_requires_processing(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    dave = make_user("dave")
    job = _upload(client, dave)
    _finish(client, queue, dave, job["id"])
    assert client.delete(f"/api/jobs/{job['id']}/translation", auth=dave).status_code == 409


def test_run_job_is_idempotent(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    gina = make_user("gina")
    job = _upload(client, gina)
    _finish(client, queue, gina, job["id"])
    client.patch(f"/api/jobs/{job['id']}/cues/1", json={"target": "edited"}, auth=gina)
    queue.run_all()  # redelivery after a worker restart must not redo finished work
    cues = client.get(f"/api/jobs/{job['id']}/cues", auth=gina).json()
    assert cues[0]["target"] == "edited"


def test_failed_job_reports_error(
    client: TestClient, make_user: Callable, queue: FakeQueue, translator: StubTranslator
) -> None:
    async def boom(*_args: object, **_kwargs: object) -> None:
        msg = "secret detail"
        raise RuntimeError(msg)

    translator.translate = boom  # type: ignore[method-assign]
    hana = make_user("hana")
    job = _upload(client, hana)
    failed = _finish(client, queue, hana, job["id"])
    assert failed["status"] == "failed"
    assert failed["error"] == "translation_failed"


def test_enqueue_failure_fails_job(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    queue.fail = True
    ivan = make_user("ivan")
    job = _upload(client, ivan)
    assert job["status"] == "failed"
    assert job["error"] == "translation_queue_failed"


def test_retranslate_failure_is_bad_gateway(
    client: TestClient, make_user: Callable, queue: FakeQueue, translator: StubTranslator
) -> None:
    async def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError

    jana = make_user("jana")
    job = _upload(client, jana)
    _finish(client, queue, jana, job["id"])
    translator.retranslate = boom  # type: ignore[method-assign]
    r = client.post(f"/api/jobs/{job['id']}/cues/1/retranslate", json={}, auth=jana)
    assert r.status_code == 502


def test_progress_is_persisted_while_running(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(translation, "_POLL_SECONDS", 0.01)
    seen: list[tuple[int | None, JobStage]] = []

    async def slow(request, progress=None):
        progress.current = 1
        await asyncio.sleep(0.1)
        with SessionLocal() as db:
            job = db.get(Job, queue.job_ids[0])
            seen.append((job.processed_cues, job.stage))
        return await StubTranslator().translate(request)

    translator.translate = slow  # type: ignore[method-assign]
    kim = make_user("kim")
    job = _upload(client, kim)
    done = _finish(client, queue, kim, job["id"])
    assert seen == [(1, JobStage.TRANSLATING)]
    assert done["status"] == "ready"
    assert done["processedCues"] == 2


def test_cancel_stops_running_translation(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(translation, "_POLL_SECONDS", 0.01)
    cancelled = []

    async def hang(*_args: object, **_kwargs: object) -> None:
        with SessionLocal() as db:  # the user cancels while the worker is busy
            db.delete(db.get(Job, queue.job_ids[0]))
            db.commit()
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            cancelled.append(True)
            raise

    translator.translate = hang  # type: ignore[method-assign]
    leo = make_user("leo")
    job = _upload(client, leo)
    asyncio.run(asyncio.wait_for(translation.run_job(job["id"]), timeout=5))
    assert cancelled == [True]


def test_ownership_isolation(client: TestClient, make_user: Callable) -> None:
    erin, frank = make_user("erin"), make_user("frank")
    job = _upload(client, erin)
    assert client.get(f"/api/jobs/{job['id']}", auth=frank).status_code == 404
    assert client.get(f"/api/jobs/{job['id']}/cues", auth=frank).status_code == 404
    assert client.delete(f"/api/jobs/{job['id']}", auth=frank).status_code == 404
    assert client.get("/api/jobs", auth=frank).json() == []


def test_upload_validation(client: TestClient) -> None:
    def post(name: str, body: bytes, source: str = "en", target: str = "de") -> int:
        return client.post(
            "/api/jobs",
            files={"file": (name, body)},
            data={"sourceLang": source, "targetLang": target},
            auth=ADMIN,
        ).status_code

    assert post("movie.txt", SRT.encode()) == 422
    assert post("movie.srt", b"\xff\xfe\x00bad") == 422
    assert post("movie.srt", b"not an srt") == 422
    assert post("movie.srt", SRT.encode(), "en", "en") == 422
    assert post("movie.srt", SRT.encode(), "en", "zz") == 422


def test_estimate_and_detect(client: TestClient) -> None:
    est = client.post("/api/jobs/estimate", json={"cueCount": 240}, auth=ADMIN).json()
    assert est == {"seconds": 10, "tokens": 1200}
    r = client.post(
        "/api/subtitles/detect-language", files={"file": ("a.srt", SRT.encode())}, auth=ADMIN
    )
    assert r.json() == {"code": "en"}


def test_temporary_password_must_be_changed_on_first_login(client: TestClient) -> None:
    r = client.post(
        "/api/admin/users",
        json={"username": "tina", "password": "temporary-1"},
        auth=ADMIN,
    )
    assert r.json()["mustChangePassword"] is True
    tina = ("tina", "temporary-1")

    # Only /auth/me and the password change work until it is replaced.
    assert client.get("/api/auth/me", auth=tina).json()["mustChangePassword"] is True
    blocked = client.get("/api/usage", auth=tina)
    assert blocked.status_code == 403
    assert blocked.json()["detail"] == "Password change required"
    assert blocked.json()["code"] == "password_change_required"
    assert client.get("/api/languages", auth=tina).status_code == 403

    change = "/api/auth/password"
    wrong = client.post(
        change, json={"currentPassword": "x", "newPassword": "new-password"}, auth=tina
    )
    assert wrong.status_code == 422
    same = client.post(
        change,
        json={"currentPassword": "temporary-1", "newPassword": "temporary-1"},
        auth=tina,
    )
    assert same.status_code == 422
    ok = client.post(
        change,
        json={"currentPassword": "temporary-1", "newPassword": "new-password"},
        auth=tina,
    )
    assert ok.status_code == 204

    tina = ("tina", "new-password")
    assert client.get("/api/auth/me", auth=tina).json()["mustChangePassword"] is False
    assert client.get("/api/usage", auth=tina).status_code == 200
    assert client.get("/api/auth/me", auth=("tina", "temporary-1")).status_code == 401


def test_admin_password_reset_is_temporary_except_for_self(
    client: TestClient, make_user: Callable
) -> None:
    uma = make_user("uma")
    uma_id = client.get("/api/auth/me", auth=uma).json()["id"]
    admin_id = client.get("/api/auth/me", auth=ADMIN).json()["id"]

    r = client.patch(
        f"/api/admin/users/{uma_id}", json={"password": "reset-12345"}, auth=ADMIN
    )
    assert r.json()["mustChangePassword"] is True
    assert client.get("/api/usage", auth=("uma", "reset-12345")).status_code == 403

    r = client.patch(f"/api/admin/users/{admin_id}", json={"password": ADMIN[1]}, auth=ADMIN)
    assert r.json()["mustChangePassword"] is False
    assert client.get("/api/usage", auth=ADMIN).status_code == 200


def test_admin_sees_any_users_usage_and_quota(client: TestClient, make_user: Callable) -> None:
    vic = make_user("vic")
    vic_id = client.get("/api/auth/me", auth=vic).json()["id"]
    admin_id = client.get("/api/auth/me", auth=ADMIN).json()["id"]

    assert client.get(f"/api/admin/users/{vic_id}/usage", auth=vic).status_code == 403
    assert client.get(f"/api/admin/users/{vic_id}/usage/records", auth=vic).status_code == 403
    summary = client.get(f"/api/admin/users/{vic_id}/usage", auth=ADMIN)
    assert summary.status_code == 200
    assert summary.json()["quota"]["used"] == 0
    assert client.get(f"/api/admin/users/{vic_id}/usage/records", auth=ADMIN).json() == []
    assert client.get("/api/admin/users/99999/usage", auth=ADMIN).status_code == 404

    # An admin can change their own quota too.
    r = client.patch(f"/api/admin/users/{admin_id}", json={"monthlyQuota": 1234}, auth=ADMIN)
    assert r.json()["monthlyQuota"] == 1234
    assert (
        client.get(f"/api/admin/users/{admin_id}/usage", auth=ADMIN).json()["quota"]["limit"]
        == 1234
    )


def test_user_locale(client: TestClient) -> None:
    assert client.get("/api/auth/me", auth=ADMIN).json()["locale"] is None

    # An admin can choose it upfront; the user can change or clear it later.
    created = client.post(
        "/api/admin/users",
        json={"username": "lenka", "password": "temporary-1", "locale": "cs"},
        auth=ADMIN,
    )
    assert created.json()["locale"] == "cs"
    lenka = ("lenka", "temporary-1")
    assert client.get("/api/auth/me", auth=lenka).json()["locale"] == "cs"

    changed = client.patch("/api/auth/me", json={"locale": "en"}, auth=lenka)
    assert changed.json()["locale"] == "en"
    cleared = client.patch("/api/auth/me", json={"locale": None}, auth=lenka)
    assert cleared.json()["locale"] is None
    assert client.patch("/api/auth/me", json={"locale": "xx"}, auth=lenka).status_code == 422
    listed = {
        u["username"]: u["locale"] for u in client.get("/api/admin/users", auth=ADMIN).json()
    }
    assert listed["lenka"] is None

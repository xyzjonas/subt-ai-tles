import time
from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import ADMIN, SRT


def _upload(client: TestClient, auth: tuple[str, str], body: bytes = SRT.encode()) -> dict:
    r = client.post(
        "/api/jobs",
        files={"file": ("movie.srt", body, "application/x-subrip")},
        data={"sourceLang": "en", "targetLang": "de"},
        auth=auth,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _wait_ready(client: TestClient, auth: tuple[str, str], job_id: str) -> dict:
    for _ in range(100):
        job = client.get(f"/api/jobs/{job_id}", auth=auth).json()
        if job["status"] != "processing":
            return job
        time.sleep(0.05)
    msg = "job never finished"
    raise AssertionError(msg)


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


def test_job_lifecycle(client: TestClient, make_user: Callable) -> None:
    bob = make_user("bob")
    job = _upload(client, bob)
    assert job["status"] == "processing"
    assert job["cueCount"] == 2

    done = _wait_ready(client, bob, job["id"])
    assert done["status"] == "ready"
    assert done["processedCues"] == 2
    assert done["model"] == "placeholder"

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
    assert [v["label"] for v in variants] == ["Literal", "Punchy / Action", "Shorter"]

    dl = client.get(f"/api/jobs/{job['id']}/download", auth=bob)
    assert dl.headers["content-disposition"] == 'attachment; filename="movie.de.srt"'
    assert "Hallo" in dl.text

    assert client.get("/api/jobs", auth=bob).json()[0]["id"] == job["id"]
    assert client.delete(f"/api/jobs/{job['id']}", auth=bob).status_code == 204
    assert client.get(f"/api/jobs/{job['id']}", auth=bob).status_code == 404


def test_cancel_translation(client: TestClient, make_user: Callable) -> None:
    carol = make_user("carol")
    many = "".join(
        f"{i}\n00:00:{i % 60:02d},000 --> 00:00:{i % 60:02d},500\nline {i}\n\n"
        for i in range(1, 400)
    )
    job = _upload(client, carol, many.encode())
    assert client.delete(f"/api/jobs/{job['id']}/translation", auth=carol).status_code == 204
    assert client.get(f"/api/jobs/{job['id']}", auth=carol).status_code == 404


def test_cancel_requires_processing(client: TestClient, make_user: Callable) -> None:
    dave = make_user("dave")
    job = _upload(client, dave)
    _wait_ready(client, dave, job["id"])
    assert client.delete(f"/api/jobs/{job['id']}/translation", auth=dave).status_code == 409


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

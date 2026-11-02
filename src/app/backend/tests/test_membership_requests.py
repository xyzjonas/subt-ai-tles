from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import ADMIN

PUBLIC = "/api/membership-requests"
ADMIN_URL = "/api/admin/membership-requests"


def _submit(client: TestClient, email: str, details: str | None = None) -> None:
    r = client.post(PUBLIC, json={"email": email, "details": details})
    assert r.status_code == 202, r.text


def _find(client: TestClient, email: str, status: str = "pending") -> dict:
    rows = client.get(ADMIN_URL, params={"status": status}, auth=ADMIN).json()
    return next(r for r in rows if r["email"] == email)


def test_submit_needs_no_sign_in_and_is_listed_for_admin(client: TestClient) -> None:
    _submit(client, "Ada@Example.com", "  I translate fan subs  ")

    row = _find(client, "ada@example.com")
    assert row["details"] == "I translate fan subs"
    assert row["status"] == "pending"
    assert row["decidedAt"] is None


def test_invalid_email_is_rejected(client: TestClient) -> None:
    for email in ("nope", "a@b", "has space@x.com", "x" * 70 + "@example.com"):
        assert client.post(PUBLIC, json={"email": email}).status_code == 422


def test_duplicate_pending_request_is_stored_once(client: TestClient) -> None:
    _submit(client, "twice@example.com")
    _submit(client, "twice@example.com")

    rows = client.get(ADMIN_URL, auth=ADMIN).json()
    assert [r["email"] for r in rows].count("twice@example.com") == 1


def test_existing_account_is_not_revealed(client: TestClient, make_user: Callable) -> None:
    make_user("taken@example.com")

    _submit(client, "taken@example.com")

    rows = client.get(ADMIN_URL, auth=ADMIN).json()
    assert "taken@example.com" not in [r["email"] for r in rows]


def test_admin_only(client: TestClient, make_user: Callable) -> None:
    kim = make_user("kim")
    _submit(client, "admin-only@example.com")
    row = _find(client, "admin-only@example.com")

    assert client.get(ADMIN_URL).status_code == 401
    assert client.get(ADMIN_URL, auth=kim).status_code == 403
    assert client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=kim).status_code == 403
    r = client.post(f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=kim)
    assert r.status_code == 403


def test_approve_creates_user_with_default_quota(client: TestClient) -> None:
    _submit(client, "grace@example.com")
    row = _find(client, "grace@example.com")

    r = client.post(
        f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=ADMIN
    )

    assert r.status_code == 201
    assert r.json()["username"] == "grace@example.com"
    assert r.json()["monthlyQuota"] == 1000
    assert r.json()["mustChangePassword"] is True
    assert client.get("/api/auth/me", auth=("grace@example.com", "temporary-1")).status_code == 200
    assert _find(client, "grace@example.com", "approved")["decidedAt"] is not None


def test_reject_creates_no_user(client: TestClient) -> None:
    _submit(client, "nope@example.com")
    row = _find(client, "nope@example.com")

    r = client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=ADMIN)

    assert r.json()["status"] == "rejected"
    assert client.get("/api/auth/me", auth=("nope@example.com", "temporary-1")).status_code == 401


def test_a_decided_request_cannot_be_decided_again(client: TestClient) -> None:
    _submit(client, "once@example.com")
    row = _find(client, "once@example.com")
    client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=ADMIN)

    r = client.post(f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=ADMIN)
    assert (r.status_code, r.json()["code"]) == (409, "membership_request_decided")
    assert client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=ADMIN).status_code == 409


def test_unknown_request(client: TestClient) -> None:
    r = client.post(f"{ADMIN_URL}/999999/reject", auth=ADMIN)
    assert (r.status_code, r.json()["code"]) == (404, "membership_request_not_found")


def test_approving_when_the_username_exists_keeps_the_request_pending(
    client: TestClient, make_user: Callable
) -> None:
    _submit(client, "late@example.com")
    row = _find(client, "late@example.com")
    make_user("late@example.com")  # an admin created the account in the meantime

    r = client.post(f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=ADMIN)

    assert (r.status_code, r.json()["code"]) == (409, "username_taken")
    assert _find(client, "late@example.com")["status"] == "pending"

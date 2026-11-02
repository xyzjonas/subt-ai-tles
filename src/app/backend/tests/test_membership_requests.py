from collections.abc import Callable, Iterator

import pytest
from app.api.membership_requests import submission_limiter
from app.ratelimit import RateLimiter, client_key
from fastapi.testclient import TestClient
from starlette.requests import Request

from tests.conftest import ADMIN

PUBLIC = "/api/membership-requests"
ADMIN_URL = "/api/admin/membership-requests"


@pytest.fixture(autouse=True)
def fresh_limiter() -> Iterator[None]:
    submission_limiter.reset()
    yield
    submission_limiter.reset()


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
    r = client.post(
        f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=kim
    )
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
    assert (
        client.get("/api/auth/me", auth=("grace@example.com", "temporary-1")).status_code
        == 200
    )
    assert _find(client, "grace@example.com", "approved")["decidedAt"] is not None


def test_reject_creates_no_user(client: TestClient) -> None:
    _submit(client, "nope@example.com")
    row = _find(client, "nope@example.com")

    r = client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=ADMIN)

    assert r.json()["status"] == "rejected"
    assert (
        client.get("/api/auth/me", auth=("nope@example.com", "temporary-1")).status_code == 401
    )


def test_a_decided_request_cannot_be_decided_again(client: TestClient) -> None:
    _submit(client, "once@example.com")
    row = _find(client, "once@example.com")
    client.post(f"{ADMIN_URL}/{row['id']}/reject", auth=ADMIN)

    r = client.post(
        f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=ADMIN
    )
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

    r = client.post(
        f"{ADMIN_URL}/{row['id']}/approve", json={"password": "temporary-1"}, auth=ADMIN
    )

    assert (r.status_code, r.json()["code"]) == (409, "username_taken")
    assert _find(client, "late@example.com")["status"] == "pending"


def _post(client: TestClient, n: int, ip: str = "203.0.113.9", via: str = "") -> int:
    headers = {"X-Forwarded-For": f"{via}{ip}"}
    return client.post(
        PUBLIC, json={"email": f"user{n}@example.com"}, headers=headers
    ).status_code


def test_per_client_limit_blocks_with_retry_after(client: TestClient) -> None:
    limit = submission_limiter.limit
    assert [_post(client, n) for n in range(limit)] == [202] * limit

    r = client.post(
        PUBLIC, json={"email": "more@example.com"}, headers={"X-Forwarded-For": "203.0.113.9"}
    )

    assert r.status_code == 429
    assert r.json()["code"] == "rate_limited"
    assert r.json()["params"]["minutes"] >= 1
    assert 0 < int(r.headers["Retry-After"]) <= 3600
    assert "more@example.com" not in [
        x["email"] for x in client.get(ADMIN_URL, auth=ADMIN).json()
    ]
    assert _post(client, 99, ip="203.0.113.10") == 202  # another client is unaffected


def test_invalid_submissions_count_too(client: TestClient) -> None:
    for _ in range(submission_limiter.limit):
        assert client.post(PUBLIC, json={"email": "nope"}).status_code == 422

    assert client.post(PUBLIC, json={"email": "ok@example.com"}).status_code == 429


def test_client_cannot_dodge_the_limit_by_spoofing_forwarded_for(client: TestClient) -> None:
    for n in range(submission_limiter.limit):
        _post(client, n, via=f"10.0.0.{n}, ")

    assert _post(client, 99, via="10.9.9.9, ") == 429


def test_global_limit_caps_all_clients_together(client: TestClient) -> None:
    allowed = submission_limiter.global_limit
    results = [_post(client, n, ip=f"198.51.100.{n}") for n in range(allowed + 1)]

    assert results == [202] * allowed + [429]


def test_limiter_window_slides() -> None:
    now = [0.0]
    limiter = RateLimiter(limit=2, global_limit=10, window=100, clock=lambda: now[0])

    assert limiter.hit("a") is None
    now[0] = 50
    assert limiter.hit("a") is None
    assert limiter.hit("a") == 50  # the first hit leaves the window in 50s
    now[0] = 100
    assert limiter.hit("a") is None


def test_blocked_client_does_not_use_up_the_global_budget() -> None:
    limiter = RateLimiter(limit=1, global_limit=2, window=100, clock=lambda: 0.0)

    assert limiter.hit("a") is None
    assert all(limiter.hit("a") is not None for _ in range(10))
    assert limiter.hit("b") is None
    assert limiter.hit("c") is not None  # only now is the global budget gone


def _request(forwarded: str | None, host: str = "172.18.0.1") -> Request:
    headers = [(b"x-forwarded-for", forwarded.encode())] if forwarded else []
    return Request({"type": "http", "headers": headers, "client": (host, 1234)})


@pytest.mark.parametrize(
    ("forwarded", "hops", "expected"),
    [
        ("1.1.1.1, 2.2.2.2", 1, "2.2.2.2"),
        ("1.1.1.1, 2.2.2.2", 2, "1.1.1.1"),
        ("1.1.1.1", 2, "172.18.0.1"),  # fewer entries than trusted proxies: don't guess
        ("1.1.1.1", 0, "172.18.0.1"),  # directly exposed: the header is ignored
        (None, 1, "172.18.0.1"),
        ("2001:db8:1:2:aaaa:bbbb:cccc:dddd", 1, "2001:db8:1:2::/64"),
    ],
)
def test_client_key(forwarded: str | None, hops: int, expected: str) -> None:
    assert client_key(_request(forwarded), hops) == expected

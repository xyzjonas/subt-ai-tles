import fakeredis
import pytest
from app.cache import RedisCache


@pytest.fixture
def client() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(decode_responses=True)


def test_roundtrip_and_miss(client: fakeredis.FakeRedis) -> None:
    cache = RedisCache(client)
    cache["k"] = "hola"

    assert cache.get("k") == "hola"
    assert cache.get("missing") is None
    assert client.get("subtaitles:translation:k") == "hola"


def test_ttl(client: fakeredis.FakeRedis) -> None:
    RedisCache(client, ttl=60)["k"] = "v"

    assert 0 < client.ttl("subtaitles:translation:k") <= 60


def test_clear_only_removes_own_keys(client: fakeredis.FakeRedis) -> None:
    cache = RedisCache(client)
    for i in range(1200):
        cache[str(i)] = "v"
    client.set("celery-task", "x")

    cache.clear()

    assert cache.get("0") is None
    assert client.keys() == ["celery-task"]

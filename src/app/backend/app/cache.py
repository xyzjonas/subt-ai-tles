"""Redis-backed translation cache, injected into the `subtaitles` translator."""

from functools import cache
from typing import cast

import redis
from subtaitles import CacheProtocol  # type: ignore[import-untyped]

from app.config import settings

_PREFIX = "subtaitles:translation:"
_SCAN_BATCH = 500


class RedisCache:
    """Implements `subtaitles.CacheProtocol`. Keys are prefixed; `clear()` drops only ours."""

    def __init__(
        self, client: redis.Redis, *, prefix: str = _PREFIX, ttl: int | None = None
    ) -> None:
        self._client = client
        self._prefix = prefix
        self._ttl = ttl

    def get(self, key: str) -> str | None:
        return cast("str | None", self._client.get(self._prefix + key))  # sync client

    def __setitem__(self, key: str, value: str) -> None:
        self._client.set(self._prefix + key, value, ex=self._ttl)

    def clear(self) -> None:
        """Delete only our own keys, never the whole DB."""
        batch: list[str] = []
        for key in self._client.scan_iter(match=f"{self._prefix}*", count=_SCAN_BATCH):
            batch.append(key)
            if len(batch) >= _SCAN_BATCH:
                self._client.delete(*batch)
                batch.clear()
        if batch:
            self._client.delete(*batch)


@cache
def get_cache() -> CacheProtocol:
    client = redis.Redis.from_url(settings.cache_redis_url, decode_responses=True)
    return RedisCache(client, ttl=settings.cache_ttl_seconds)

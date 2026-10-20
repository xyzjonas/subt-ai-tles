from typing import Protocol

from diskcache import Cache

from .environment import env

disk_cache = Cache(env.CACHE_DIR.value)


class CacheProtocol(Protocol):
    def get(self, key: str) -> str | None: ...

    def __setitem__(self, key: str, value: str) -> None: ...

    def clear(self) -> None: ...

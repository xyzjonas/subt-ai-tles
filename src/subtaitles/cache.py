from typing import Protocol, TypeVar

from diskcache import Cache

from .environment import env

disk_cache = Cache(env.CACHE_DIR.value)


T = TypeVar("T")


class CacheProtocol(Protocol[T]):
    def get(self, key: str) -> T: ...

    def __setattr__(self, key: str, value: T) -> None: ...

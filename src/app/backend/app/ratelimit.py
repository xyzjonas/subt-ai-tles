"""In-process sliding-window rate limiting for the public endpoints.

State lives in this process, which is right for the shipped setup (one uvicorn behind nginx).
It resets on restart, and would be per-worker if the web app were ever scaled out.
"""

import ipaddress
import math
import threading
import time
from collections import deque
from collections.abc import Callable

from fastapi import Request

from app.config import settings

_MAX_KEY_LENGTH = 64


class RateLimiter:
    """At most `limit` hits per `window` seconds for each key, and `global_limit` overall.

    Only allowed hits are recorded, so a blocked client can't use up the shared budget.
    """

    def __init__(
        self,
        limit: int,
        global_limit: int,
        window: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.global_limit = global_limit
        self.window = window
        self._clock = clock
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = {}
        self._all: deque[float] = deque()

    def _prune(self, hits: deque[float], now: float) -> None:
        while hits and hits[0] <= now - self.window:
            hits.popleft()

    def _wait(self, hits: deque[float], now: float) -> int:
        return max(1, math.ceil(hits[0] + self.window - now))

    def hit(self, key: str) -> int | None:
        """Record a hit; return None if allowed, else the seconds until it would be."""
        now = self._clock()
        with self._lock:
            mine = self._hits.setdefault(key, deque())
            self._prune(mine, now)
            self._prune(self._all, now)
            for hits, limit in ((mine, self.limit), (self._all, self.global_limit)):
                if len(hits) >= limit:
                    if not mine:  # don't keep a key around for a hit we turned away
                        del self._hits[key]
                    return self._wait(hits, now) if hits else math.ceil(self.window)
            mine.append(now)
            self._all.append(now)
            self._forget_idle(now)
            return None

    def _forget_idle(self, now: float) -> None:
        # Keeps the table bounded by the global limit rather than by distinct clients seen.
        for key in [
            k for k, hits in self._hits.items() if not hits or hits[-1] <= now - self.window
        ]:
            del self._hits[key]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
            self._all.clear()


def client_key(request: Request, trusted_proxy_hops: int | None = None) -> str:
    """Who is calling: the address the nearest trusted proxy saw.

    Each proxy appends the address it received the request from to `X-Forwarded-For`, so with
    N trusted proxies the Nth entry from the right is the client; anything left of it is
    client-supplied and can't be trusted. IPv6 clients are grouped by /64, since a single
    subscriber controls a whole one.
    """
    hops = settings.trusted_proxy_hops if trusted_proxy_hops is None else trusted_proxy_hops
    forwarded = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",")]
    forwarded = [p for p in forwarded if p]
    if hops > 0 and len(forwarded) >= hops:
        raw = forwarded[-hops]
    else:
        raw = request.client.host if request.client else "unknown"
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        return raw[:_MAX_KEY_LENGTH]
    if isinstance(address, ipaddress.IPv6Address):
        return str(ipaddress.ip_network(f"{address}/64", strict=False))
    return str(address)

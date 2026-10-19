from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from subtaitles.models import TranslationRequest, TranslationResponse


class Progress(Protocol):
    total: int
    current: int


class TranslateProtocol(Protocol):
    async def translate(
        self,
        request: TranslationRequest,
        progress: Progress | None = None,
    ) -> TranslationResponse: ...

    async def summarize(self, request: TranslationRequest) -> str: ...


class SummaryStoreProtocol(Protocol):
    """Persistence for story briefs, keyed by ``TitleMetadata.key``."""

    async def get(self, key: str) -> str | None: ...

    async def put(self, key: str, summary: str) -> None: ...

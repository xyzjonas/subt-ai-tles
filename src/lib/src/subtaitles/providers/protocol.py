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

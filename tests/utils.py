from __future__ import annotations

from typing import TYPE_CHECKING

from subtaitles.models import TranslatedSegment, TranslationResponse

if TYPE_CHECKING:
    from subtaitles.models import TranslationRequest
    from subtaitles.providers.protocol import Progress


class MockedTranslator:
    @staticmethod
    async def translate(
        request: TranslationRequest,
        progress: Progress | None = None,  # noqa: ARG004
    ) -> TranslationResponse:
        segments = tuple(
            TranslatedSegment(
                index=seg.index,
                source=seg.text,
                translation=seg.text,
                status="translated",
            )
            for seg in request.segments
        )
        return TranslationResponse(
            segments=segments,
            source=request.source,
            target=request.target,
        )

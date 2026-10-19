from __future__ import annotations

from typing import TYPE_CHECKING

from libretranslatepy import LibreTranslateAPI

from subtaitles.environment import env
from subtaitles.models import TranslatedSegment, TranslationResponse

if TYPE_CHECKING:
    from subtaitles.models import TranslationRequest
    from subtaitles.providers.protocol import Progress

DELIMITER = "\n\n"


class LibreTranslateTranslator:
    def __init__(self, base_url: str | None = None) -> None:
        self.client = LibreTranslateAPI(base_url or env.LIBRETRANSLATE_API_URL(strict=True))

    async def translate(
        self,
        request: TranslationRequest,
        progress: Progress | None = None,  # noqa: ARG002
    ) -> TranslationResponse:
        text = [seg.text for seg in request.segments]
        result = self.client.translate(
            DELIMITER.join(text),
            source=request.source.language.iso,
            target=request.target.language.iso,
        )
        translations = result.split(DELIMITER)
        segments = tuple(
            TranslatedSegment(
                index=seg.index,
                source=seg.text,
                translation=t,
                status="translated",
            )
            for seg, t in zip(request.segments, translations, strict=False)
        )
        return TranslationResponse(
            segments=segments,
            source=request.source,
            target=request.target,
        )

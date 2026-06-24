from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from subtaitles.environment import env
from subtaitles.models import TranslatedSegment, TranslationResponse

if TYPE_CHECKING:
    from subtaitles.models import TranslationRequest
    from subtaitles.providers.protocol import Progress


class PydanticAiTranslator:
    @staticmethod
    async def translate(
        request: TranslationRequest,
        progress: Progress | None = None,  # noqa: ARG004
        model: str | None = None,
    ) -> TranslationResponse:
        source, target = request.source, request.target
        agent = Agent(
            model=model or env.OPENAI_MODEL(strict=True),
            instructions=f"Translate subtitles from {source.value.english} to "
            f"{target.value.english} accurately while "
            "maintaining the original meaning and tone. Use natural-sounding "
            "phrases and idioms that accurately convey the meaning "
            "of the original text.",
            output_type=list[str],
        )
        text = [seg.text for seg in request.segments]
        translations = (await agent.run(text)).output
        segments = tuple(
            TranslatedSegment(
                index=seg.index,
                source=seg.text,
                translation=t,
                status="translated",
            )
            for seg, t in zip(request.segments, translations, strict=False)
        )
        return TranslationResponse(segments=segments, source=source, target=target)

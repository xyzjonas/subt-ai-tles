from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from openai import AsyncOpenAI

from subtaitles.cache import CacheProtocol, disk_cache
from subtaitles.environment import env
from subtaitles.imports import batched
from subtaitles.models import TranslatedSegment, TranslationResponse

if TYPE_CHECKING:
    from collections.abc import Iterable

    from subtaitles.language import Lang
    from subtaitles.models import Segment, TranslationRequest
    from subtaitles.providers.protocol import Progress


logger = logging.getLogger(__name__)

DELIMITER = "---"
MIN_RETRIES_TO_LOG = 3


class OpenAiTranslator:
    context = """Translate subtitles from {lang_from} to {lang_to} accurately while
maintaining the original meaning and tone. Use natural-sounding phrases and idioms
that accurately convey the meaning of the original text. KEEP the delimiters '{delimiter}'
in place to indicate item borders! Keep newlines \\n and \\r and do not consider them item
delimiters,\nnewline characters are allowed within a single sentence. Response can't start or
end with a {delimiter}. Make sure that the number of lines separated by {delimiter} is equal.
"""

    def __init__(
        self,
        model: str | None = None,
        openapi_key: str | None = None,
        openapi_org: str | None = None,
        batch_size: int = 10,
        cache: CacheProtocol = None,
    ) -> None:
        self.model = model or env.OPENAI_MODEL(strict=True)
        self.client = AsyncOpenAI(
            api_key=openapi_key or env.OPENAI_API_KEY(strict=True),
            organization=openapi_org or env.OPENAI_ORG_ID(strict=True),
        )
        self.batch_size = batch_size
        self.cache = cache or disk_cache

    def get_completion(
        self,
        lang_from: Lang,
        lang_to: Lang,
        items: Iterable[str],
    ) -> dict:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.context.format(
                        lang_from=lang_from.language.english,
                        lang_to=lang_to.language.english,
                        delimiter=DELIMITER,
                    ),
                },
                {"role": "user", "content": "---".join(items)},
            ],
        }

    async def process_batch(  # noqa: PLR0913
        self,
        segments: list[Segment],
        source: Lang,
        target: Lang,
        retries_left: int = 10,
        batch_id: int = 0,
        progress: Progress | None = None,
    ) -> list[TranslatedSegment]:
        if retries_left < MIN_RETRIES_TO_LOG:
            logger.debug("Processing batch %d retries-left=%d", batch_id, retries_left)

        text = [seg.text for seg in segments]
        completion = self.get_completion(source, target, text)
        response = await self.client.chat.completions.create(**completion)
        if not response.choices:
            if retries_left > 0:
                return await self.process_batch(
                    segments, source, target, retries_left - 1, batch_id, progress
                )
            msg = "GPT returned no predictions, unexpected..."
            raise ValueError(msg)

        translations = [
            line for line in response.choices[0].message.content.split(DELIMITER) if line
        ]
        if len(translations) != len(segments):
            if retries_left > 0:
                return await self.process_batch(
                    segments, source, target, retries_left - 1, batch_id, progress
                )
            msg = (
                f"Input lines count doesn't match output's line count! "
                f"{text} --> {translations}"
            )
            raise ValueError(msg)

        logger.debug("[OK] batch %d completed, retries-left=%d", batch_id, retries_left)
        if progress:
            progress.current += 1

        results = []
        for seg, translation in zip(segments, translations, strict=True):
            key = seg.cache_key(source, target, self.model)
            self.cache[key] = translation
            results.append(
                TranslatedSegment(
                    index=seg.index,
                    source=seg.text,
                    translation=translation,
                    status="translated",
                )
            )
        return results

    async def translate(
        self,
        request: TranslationRequest,
        progress: Progress | None = None,
    ) -> TranslationResponse:
        source, target = request.source, request.target
        cached_results: dict[int, TranslatedSegment] = {}
        uncached: list[Segment] = []

        for seg in request.segments:
            key = seg.cache_key(source, target, self.model)
            cached = self.cache.get(key)
            if cached is not None:
                cached_results[seg.index] = TranslatedSegment(
                    index=seg.index,
                    source=seg.text,
                    translation=cached,
                    status="translated",
                )
            else:
                uncached.append(seg)

        tasks = [
            self.process_batch(list(batch), source, target, batch_id=i, progress=progress)
            for i, batch in enumerate(batched(uncached, self.batch_size, strict=False))
        ]

        if progress:
            # progress.total = len(tasks) + len(cached_results)
            progress.total = len(request.segments)

        all_results = dict(cached_results)
        for batch_results in await asyncio.gather(*tasks):
            for seg in batch_results:
                all_results[seg.index] = seg

        ordered = tuple(all_results[seg.index] for seg in request.segments)
        return TranslationResponse(segments=ordered, source=source, target=target)

from __future__ import annotations

import asyncio
import json
import random
import re
from typing import TYPE_CHECKING

from loguru import logger
from openai import AsyncOpenAI, RateLimitError
from pydantic import BaseModel, ValidationError

from subtaitles.cache import CacheProtocol, disk_cache
from subtaitles.environment import env
from subtaitles.imports import batched
from subtaitles.models import TranslatedSegment, TranslationResponse

if TYPE_CHECKING:
    from subtaitles.models import Segment, TranslationRequest
    from subtaitles.providers.protocol import Progress


DELIMITER = "---"
API_RETRIES = 10
MIN_RETRIES_TO_LOG = 3


class OpenAiTranslation(BaseModel):
    id: int
    text: str


class OpenAiResponse(BaseModel):
    translations: list[OpenAiTranslation]

    @property
    def mapping(self) -> dict[int, str]:
        return {t.id: t.text for t in self.translations}


_RETRY_RE = re.compile(r"try again in\s+(?:(\d+(?:\.\d+)?)m(?!s))?\s*(?:(\d+(?:\.\d+)?)s)?\s*(?:(\d+(?:\.\d+)?)ms)?", re.I)

def get_retry_delay(e: RateLimitError, default: float = 1.0) -> float:
    # 1. Prefer headers if present (most reliable)
    headers = getattr(getattr(e, "response", None), "headers", None)
    if headers:
        if v := headers.get("retry-after-ms"):
            return float(v) / 1000
        if v := headers.get("retry-after"):
            return float(v)

    # 2. Fall back to parsing the message text
    msg = ""
    if isinstance(e.body, dict):
        msg = e.body.get("message", "") or ""
    msg = msg or str(e)

    m = _RETRY_RE.search(msg)
    if m and any(m.groups()):
        minutes, seconds, millis = (float(g) if g else 0.0 for g in m.groups())
        return minutes * 60 + seconds + millis / 1000

    return default


class OpenAiTranslator:
    #     context = """Translate subtitles from {lang_from} to {lang_to} accurately while
    # maintaining the original meaning and tone. Use natural-sounding phrases and idioms
    # that accurately convey the meaning of the original text. KEEP the delimiters '{delimiter}'
    # in place to indicate item borders! Keep newlines \\n and \\r and do not consider them item
    # delimiters,\nnewline characters are allowed within a single sentence. Response can't start or
    # end with a {delimiter}. Make sure that the number of lines separated by {delimiter} is equal.
    # """
    SYSTEM = """You are a professional subtitle translator. Translate from {lang_from} to {lang_to}.

    Input is a JSON object with "items" (to translate) and optional "context_before" /
    "context_after" (surrounding lines, for understanding only, do NOT translate them).

    Rules:
    - Return exactly one translation per item, using the same "id".
    - NEVER merge, split, drop or reorder items. Many items are sentence fragments;
      translate each fragment as its own unit, choosing wording that flows naturally
      from the previous item into the next.
    - Preserve line breaks (\\n) within an item where they make sense in the target language.
    - Keep meaning, tone and register. Use natural idioms.
    """

    RESPONSE_FORMAT = {
        "type": "json_schema",
        "json_schema": {
            "name": "subtitle_translations",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "translations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "text": {"type": "string"},
                            },
                            "required": ["id", "text"],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["translations"],
                "additionalProperties": False,
            },
        },
    }

    def __init__(
        self,
        model: str | None = None,
        openapi_key: str | None = None,
        openapi_org: str | None = None,
        batch_size: int = 30,
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
        segments: list[Segment],
        request: TranslationRequest,
    ) -> dict:
        payload = {
            "context_before": f"Title: {request.metadata.title}, {request.metadata.description}"
            if request.metadata
            else "",
            "items": [{"id": s.index, "text": s.text} for s in segments],
            "context_after": "",
        }

        return {
            "model": self.model,
            "temperature": 0,
            "response_format": self.RESPONSE_FORMAT,
            "messages": [
                {
                    "role": "system",
                    "content": self.SYSTEM.format(
                        lang_from=request.source.language.english,
                        lang_to=request.target.language.english,
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }

    async def __call(self, completion: dict, retries_left: int) -> OpenAiResponse:
        try:
            response = await self.client.chat.completions.create(**completion)
        except RateLimitError as e:
            if retries_left <= 0:
                logger.exception(e)
                raise
            random_coefficient = random.randint(5,30)
            delay = get_retry_delay(e)
            delay = delay * random_coefficient * (API_RETRIES + 1 - retries_left)
            logger.warning(f"Rate limited, retrying in {delay:.3f}s ({retries_left} retries left)")
            await asyncio.sleep(delay)
            return await self.__call(completion, retries_left=retries_left - 1)

        try:
            data = json.loads(response.choices[0].message.content)
            return OpenAiResponse(**data)
        except (ValidationError, json.JSONDecodeError, KeyError, TypeError, IndexError) as e:
            logger.error(f"Malformed response: {e}")
            if retries_left > 0:
                await asyncio.sleep(0.1)
                return await self.__call(completion, retries_left=retries_left - 1)
            raise

    async def process_batch(  # noqa: PLR0913
        self,
        segments: list[Segment],
        *,
        request: TranslationRequest,
        retries_left: int = 10,
        batch_id: int = 0,
        progress: Progress | None = None,
    ) -> list[TranslatedSegment]:
        logger.debug(f"Processing batch {batch_id} retries-left={retries_left}")
        if retries_left < MIN_RETRIES_TO_LOG:
            logger.debug(f"Processing batch {batch_id} retries-left={retries_left}")

        completion = self.get_completion(segments, request)
        response = await self.__call(completion, retries_left=API_RETRIES)

        results, missing = [], []
        for seg in segments:
            text = response.mapping.get(seg.index)
            if text is None or not text.strip():
                missing.append(seg)
            else:
                self.cache[seg.cache_key(request.source, request.target, self.model)] = text
                results.append(
                    TranslatedSegment(
                        index=seg.index, source=seg.text, translation=text, status="translated"
                    )
                )

        if missing:
            if retries_left <= 0:
                raise ValueError(f"No translation for ids {[s.index for s in missing]}")

            results += await self.process_batch(
                missing,
                request=request,
                retries_left=retries_left - 1,
                batch_id=batch_id,
                progress=progress,
            )

        logger.debug(f"[OK] batch {batch_id} completed, retries-left={retries_left}")
        if progress:
            progress.current += 1

        if len(segments) != len(results):
            raise ValueError(f"Result count doesn't match: {segments=} != {results=}")

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
                progress.current += 1
                cached_results[seg.index] = TranslatedSegment(
                    index=seg.index,
                    source=seg.text,
                    translation=cached,
                    status="translated",
                )
            else:
                uncached.append(seg)

        tasks = [
            self.process_batch(list(batch), request=request, batch_id=i, progress=progress)
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

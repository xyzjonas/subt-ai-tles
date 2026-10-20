from __future__ import annotations

import asyncio
import json
import random
import re
from collections import Counter
from typing import TYPE_CHECKING

from loguru import logger
from openai import AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field, ValidationError

from subtaitles.cache import CacheProtocol, disk_cache
from subtaitles.environment import env
from subtaitles.imports import batched
from subtaitles.language import find_lang
from subtaitles.models import (
    RetranslationResponse,
    TranslatedSegment,
    TranslationResponse,
    TranslationVariant,
    Usage,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from subtaitles.language import Lang
    from subtaitles.models import Segment, TranslationRequest
    from subtaitles.providers.protocol import Progress


DELIMITER = "---"
API_RETRIES = 10
MIN_RETRIES_TO_LOG = 3


class OpenAiTranslation(BaseModel):
    id: int
    text: str


class OpenAiResponse(BaseModel):
    source_language: str = Field(
        description="ISO 639-1 code of the language the input items are written in"
    )
    translations: list[OpenAiTranslation]

    @property
    def mapping(self) -> dict[int, str]:
        return {t.id: t.text for t in self.translations}


class OpenAiVariant(BaseModel):
    label: str
    text: str


class OpenAiVariants(BaseModel):
    variants: list[OpenAiVariant]


class OpenAiSummary(BaseModel):
    summary: str


class UsageMeter:
    """Sums the usage and the detected languages of the calls of one ``translate()``."""

    def __init__(self) -> None:
        self.usage = Usage()
        self.languages: Counter[Lang] = Counter()

    @property
    def source(self) -> Lang | None:
        return self.languages.most_common(1)[0][0] if self.languages else None

    def add(self, usage: Usage) -> None:
        self.usage += usage


_RETRY_RE = re.compile(
    r"try again in\s+(?:(\d+(?:\.\d+)?)m(?!s))?"
    r"\s*(?:(\d+(?:\.\d+)?)s)?\s*(?:(\d+(?:\.\d+)?)ms)?",
    re.IGNORECASE,
)


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
    SYSTEM = """You are a professional subtitle translator. Translate into {lang_to}. The
    source language is not given: infer it from the items and report it as "source_language".

    Input is a JSON object with "items" (to translate) and optional "context_before" /
    "context_after" (surrounding lines, for understanding only, do NOT translate them) and an
    optional "story_brief" (who is who, plot, settings; background only, never translate or
    output it). Use the brief to pick correct gender, formality/address forms and terminology.

    Rules:
    - Return exactly one translation per item, using the same "id".
    - NEVER merge, split, drop or reorder items. Many items are sentence fragments;
      translate each fragment as its own unit, choosing wording that flows naturally
      from the previous item into the next.
    - Preserve line breaks (\\n) within an item where they make sense in the target language.
    - Keep meaning, tone and register. Use natural idioms.
    """

    SUMMARY_SYSTEM = """You are preparing a story brief for a subtitle translator. Input is the
    complete subtitle script of one {title}, one "index|text" line per cue. Write the
    brief in English. It is attached to every translation request, so it must be as concise and
    information-dense as possible: telegraphic notes, no filler, at most {max_words} words.

    Cover only what helps translate the cues correctly:
    - Characters: name, gender, role, relationships, and who addresses whom formally or
      informally.
    - Premise and storyline in a few beats.
    - Settings, time period, genre and tone/register.
    - Recurring names, terms and jargon that must be rendered consistently.
    Do not translate the script and do not quote it.
    """

    SUMMARY_MAX_WORDS = 300
    SUMMARY_MAX_CHARS = 400_000  # ~100k tokens, longer scripts are truncated

    RETRANSLATE_SYSTEM = """You are a professional subtitle translator. Translate the subtitle
    "text" into {lang_to}. Input is a JSON object with the subtitle "text", the
    surrounding lines ("context_before" / "context_after", for understanding only, do NOT
    translate them) and the requested "variants". Return exactly one translation per requested
    variant, reusing its "label" and following its "instruction". Preserve line breaks (\\n)
    where they make sense in the target language.
    """

    VARIANT_STYLES = {  # noqa: RUF012
        "Literal": "Stay as close to the original wording as the target language allows.",
        "Punchy / Action": "Short, energetic phrasing suited to fast action scenes.",
        "Shorter": "As concise as possible while keeping the meaning, for fast reading.",
    }

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        model: str | None = None,
        openapi_key: str | None = None,
        openapi_org: str | None = None,
        batch_size: int = 120,
        cache: CacheProtocol | None = None,
        temperature: float | None = 0,
    ) -> None:
        self.model = model or env.OPENAI_MODEL(strict=True)
        self.client = AsyncOpenAI(
            api_key=openapi_key or env.OPENAI_API_KEY(strict=True),
            organization=openapi_org or env.OPENAI_ORG_ID(),
        )
        self.batch_size = batch_size
        # None leaves it to the model (some models only accept their default)
        self.temperature = temperature
        self.cache = disk_cache if cache is None else cache
        # cumulative over the translator's lifetime, also covers calls that ended in an error
        self.usage = Usage()

    def _sampling(self) -> dict:
        return {} if self.temperature is None else {"temperature": self.temperature}

    def get_completion(
        self,
        segments: list[Segment],
        request: TranslationRequest,
    ) -> dict:
        meta = request.metadata
        payload = {
            "context_before": f"Title: {meta.title}, {meta.description}" if meta else "",
            "items": [{"id": s.index, "text": s.text} for s in segments],
            "context_after": "",
        }
        if request.summary:
            payload["story_brief"] = request.summary

        return {
            "model": self.model,
            **self._sampling(),
            "text_format": OpenAiResponse,
            "input": [
                {
                    "role": "system",
                    "content": self.SYSTEM.format(lang_to=request.target.language.english),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }

    def _track(self, response: object, meter: UsageMeter | None = None) -> Usage:
        """Add the tokens reported by a completion to the translator (and call) totals."""
        raw = getattr(response, "usage", None)
        usage = Usage(
            prompt_tokens=getattr(raw, "input_tokens", 0) or 0,
            completion_tokens=getattr(raw, "output_tokens", 0) or 0,
        )
        self.usage += usage
        if meter:
            meter.add(usage)
        return usage

    async def __call(
        self, completion: dict, retries_left: int, meter: UsageMeter | None = None
    ) -> OpenAiResponse:
        try:
            response = await self.client.responses.parse(**completion)
        except RateLimitError as e:
            if retries_left <= 0:
                logger.exception(e)
                raise
            random_coefficient = random.randint(5, 30)  # noqa: S311 - backoff jitter
            delay = get_retry_delay(e)
            delay = delay * random_coefficient * (API_RETRIES + 1 - retries_left)
            logger.warning(
                f"Rate limited, retrying in {delay:.3f}s ({retries_left} retries left)"
            )
            await asyncio.sleep(delay)
            return await self.__call(completion, retries_left=retries_left - 1, meter=meter)
        except ValidationError as e:
            logger.error(f"Malformed response: {e}")
            if retries_left <= 0:
                raise
            await asyncio.sleep(0.1)
            return await self.__call(completion, retries_left=retries_left - 1, meter=meter)

        self._track(response, meter)
        if response.output_parsed is None:
            logger.error("Malformed response: nothing parsed (refusal or incomplete output)")
            if retries_left > 0:
                await asyncio.sleep(0.1)
                return await self.__call(
                    completion, retries_left=retries_left - 1, meter=meter
                )
            msg = "No parsed output returned"
            raise ValueError(msg)
        return response.output_parsed

    async def process_batch(  # noqa: PLR0913
        self,
        segments: list[Segment],
        *,
        request: TranslationRequest,
        retries_left: int = 10,
        batch_id: int = 0,
        progress: Progress | None = None,
        meter: UsageMeter | None = None,
    ) -> list[TranslatedSegment]:
        logger.debug(f"Processing batch {batch_id} retries-left={retries_left}")
        if retries_left < MIN_RETRIES_TO_LOG:
            logger.debug(f"Processing batch {batch_id} retries-left={retries_left}")

        completion = self.get_completion(segments, request)
        response = await self.__call(completion, retries_left=API_RETRIES, meter=meter)

        if meter and (language := find_lang(response.source_language)):
            meter.languages[language] += 1

        results, missing = [], []
        for seg in segments:
            text = response.mapping.get(seg.index)
            if text is None or not text.strip():
                missing.append(seg)
            else:
                self.cache[seg.cache_key(request.target, self.model)] = text
                results.append(
                    TranslatedSegment(
                        index=seg.index, source=seg.text, translation=text, status="translated"
                    )
                )

        if progress:
            progress.current += len(results)

        if missing:
            if retries_left <= 0:
                msg = f"No translation for ids {[s.index for s in missing]}"
                raise ValueError(msg)

            results += await self.process_batch(
                missing,
                request=request,
                retries_left=retries_left - 1,
                batch_id=batch_id,
                progress=progress,
                meter=meter,
            )

        logger.debug(f"[OK] batch {batch_id} completed, retries-left={retries_left}")

        if len(segments) != len(results):
            msg = f"Result count doesn't match: {segments=} != {results=}"
            raise ValueError(msg)

        return results

    async def retranslate(
        self,
        text: str,
        *,
        target: Lang,
        prompt: str | None = None,
        context_before: Sequence[str] = (),
        context_after: Sequence[str] = (),
    ) -> RetranslationResponse:
        """Alternative translations of a single subtitle.

        With a ``prompt`` a single "Custom" variant follows that instruction, otherwise one
        variant per entry of ``VARIANT_STYLES`` is returned.
        """
        styles = {"Custom": prompt} if prompt else self.VARIANT_STYLES
        payload = {
            "text": text,
            "context_before": list(context_before),
            "context_after": list(context_after),
            "variants": [
                {"label": label, "instruction": hint} for label, hint in styles.items()
            ],
        }
        response = await self.client.responses.parse(
            model=self.model,
            **self._sampling(),
            text_format=OpenAiVariants,
            input=[
                {
                    "role": "system",
                    "content": self.RETRANSLATE_SYSTEM.format(lang_to=target.language.english),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        )
        usage = self._track(response)
        parsed = response.output_parsed
        variants = (
            [TranslationVariant(v.label, v.text) for v in parsed.variants] if parsed else []
        )
        if not variants:
            msg = "No variants returned"
            raise ValueError(msg)
        return RetranslationResponse(variants=variants, usage=usage, model=self.model)

    async def summarize(self, request: TranslationRequest) -> str:
        """Concise English story brief of the whole script, used as context for every batch."""
        script = "\n".join(f"{s.index}|{s.text}" for s in request.segments)
        completion = {
            "model": self.model,
            **self._sampling(),
            "text_format": OpenAiSummary,
            "input": [
                {
                    "role": "system",
                    "content": self.SUMMARY_SYSTEM.format(
                        title=request.metadata.title if request.metadata else "title",
                        max_words=self.SUMMARY_MAX_WORDS,
                    ),
                },
                {"role": "user", "content": script[: self.SUMMARY_MAX_CHARS]},
            ],
        }
        response = await self.__call(completion, retries_left=API_RETRIES)
        summary = response.summary.strip()
        if not summary:
            msg = "Empty summary returned"
            raise ValueError(msg)
        return summary

    async def translate(
        self,
        request: TranslationRequest,
        progress: Progress | None = None,
    ) -> TranslationResponse:
        target = request.target
        cached_results: dict[int, TranslatedSegment] = {}
        uncached: list[Segment] = []

        if progress:
            progress.total = len(request.segments)

        for seg in request.segments:
            key = seg.cache_key(target, self.model)
            cached = self.cache.get(key)
            if cached is not None:
                if progress:
                    progress.current += 1
                cached_results[seg.index] = TranslatedSegment(
                    index=seg.index,
                    source=seg.text,
                    translation=cached,
                    status="translated",
                )
            else:
                uncached.append(seg)

        meter = UsageMeter()
        tasks = [
            self.process_batch(
                list(batch), request=request, batch_id=i, progress=progress, meter=meter
            )
            for i, batch in enumerate(batched(uncached, self.batch_size, strict=False))
        ]

        all_results = dict(cached_results)
        for batch_results in await asyncio.gather(*tasks):
            for seg in batch_results:
                all_results[seg.index] = seg

        ordered = tuple(all_results[seg.index] for seg in request.segments)
        return TranslationResponse(
            segments=ordered,
            target=target,
            source=meter.source,
            usage=meter.usage,
            model=self.model,
        )

from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from subtaitles import (
    Lang,
    OpenAiTranslator,
    ProgressData,
    Segment,
    SummaryStatus,
    TitleMetadata,
    TranslationRequest,
    Usage,
)
from subtaitles.translate import add_summary
from subtaitles.providers.openai import (
    OpenAiResponse,
    OpenAiSummary,
    OpenAiTranslation,
    OpenAiVariant,
    OpenAiVariants,
)


def _completion(parsed: BaseModel) -> SimpleNamespace:
    usage = SimpleNamespace(input_tokens=100, output_tokens=20)
    return SimpleNamespace(output_parsed=parsed, usage=usage)


class FakeResponses:
    """Echoes every requested item upper-cased, like a well-behaved model."""

    def __init__(self) -> None:
        self.calls = 0

    async def parse(self, **kwargs: dict) -> SimpleNamespace:
        self.calls += 1
        if kwargs["text_format"] is OpenAiSummary:
            self.script = kwargs["input"][1]["content"]
            return _completion(OpenAiSummary(summary="  Ann is the boss.  "))
        payload = json.loads(kwargs["input"][1]["content"])
        if "variants" in payload:
            variants = [
                OpenAiVariant(label=v["label"], text=payload["text"].upper())
                for v in payload["variants"]
            ]
            return _completion(OpenAiVariants(variants=variants))
        items = [OpenAiTranslation(id=i["id"], text=i["text"].upper()) for i in payload["items"]]
        return _completion(OpenAiResponse(translations=items))


def _translator(cache: dict, responses: FakeResponses) -> OpenAiTranslator:
    translator = OpenAiTranslator(model="test-model", openapi_key="key", cache=cache)
    translator.client = SimpleNamespace(responses=responses)  # type: ignore[assignment]
    return translator


def _request(count: int) -> TranslationRequest:
    segments = tuple(Segment(index=i, text=f"line {i}") for i in range(count))
    return TranslationRequest(segments=segments, source=Lang.EN, target=Lang.DE)


@pytest.mark.asyncio
async def test_progress_counts_segments_not_batches() -> None:
    translator = _translator({}, FakeResponses())
    progress = ProgressData(total=0, current=0)

    response = await translator.translate(_request(70), progress)

    assert len(response) == 70
    assert progress.total == 70
    assert progress.current == 70  # three batches (30 + 30 + 10), counted in segments


@pytest.mark.asyncio
async def test_progress_includes_cached_segments() -> None:
    cache: dict = {}
    request = _request(40)
    await _translator(cache, FakeResponses()).translate(request)

    responses = FakeResponses()
    progress = ProgressData(total=0, current=0)
    await _translator(cache, responses).translate(request, progress)

    assert responses.calls == 0
    assert progress.current == progress.total == 40


@pytest.mark.asyncio
async def test_cached_segments_work_without_progress_object() -> None:
    cache: dict = {}
    request = _request(5)
    await _translator(cache, FakeResponses()).translate(request)

    response = await _translator(cache, FakeResponses()).translate(request, None)

    assert [s.translation for s in response] == [f"LINE {i}" for i in range(5)]


def test_organization_is_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_ORG_ID", raising=False)

    OpenAiTranslator(model="test-model", openapi_key="key", cache={})


@pytest.mark.asyncio
async def test_retranslate_returns_default_variants() -> None:
    translator = _translator({}, FakeResponses())

    variants = (await translator.retranslate("hello", source=Lang.EN, target=Lang.DE)).variants

    assert [v.label for v in variants] == list(OpenAiTranslator.VARIANT_STYLES)
    assert all(v.text == "HELLO" for v in variants)


@pytest.mark.asyncio
async def test_retranslate_with_prompt_returns_single_custom_variant() -> None:
    translator = _translator({}, FakeResponses())

    variants = (
        await translator.retranslate(
            "hello", source=Lang.EN, target=Lang.DE, prompt="sound like a pirate"
        )
    ).variants

    assert [v.label for v in variants] == ["Custom"]


@pytest.mark.asyncio
async def test_translate_sums_usage_over_batches() -> None:
    translator = _translator({}, FakeResponses())

    response = await translator.translate(_request(70))  # three batches

    assert response.model == "test-model"
    assert response.usage == Usage(prompt_tokens=300, completion_tokens=60)
    assert translator.usage == response.usage


@pytest.mark.asyncio
async def test_cached_translation_uses_no_tokens() -> None:
    cache: dict = {}
    request = _request(5)
    await _translator(cache, FakeResponses()).translate(request)

    response = await _translator(cache, FakeResponses()).translate(request)

    assert response.usage == Usage()


@pytest.mark.asyncio
async def test_missing_usage_counts_as_zero() -> None:
    class NoUsage(FakeResponses):
        async def parse(self, **kwargs: dict) -> SimpleNamespace:
            response = await super().parse(**kwargs)
            del response.usage
            return response

    response = await _translator({}, NoUsage()).translate(_request(3))

    assert response.usage == Usage()


@pytest.mark.asyncio
async def test_retranslate_reports_usage() -> None:
    translator = _translator({}, FakeResponses())

    response = await translator.retranslate("hello", source=Lang.EN, target=Lang.DE)

    assert response.model == "test-model"
    assert response.usage == Usage(prompt_tokens=100, completion_tokens=20)
    assert translator.usage == response.usage


def test_temperature_is_sent_unless_unset() -> None:
    request = _request(1)
    default = OpenAiTranslator(model="test-model", openapi_key="key", cache={})
    unset = OpenAiTranslator(model="test-model", openapi_key="key", cache={}, temperature=None)
    warm = OpenAiTranslator(model="test-model", openapi_key="key", cache={}, temperature=0.7)

    assert default.get_completion(list(request.segments), request)["temperature"] == 0
    assert "temperature" not in unset.get_completion(list(request.segments), request)
    assert warm.get_completion(list(request.segments), request)["temperature"] == 0.7  # noqa: PLR2004


@pytest.mark.asyncio
async def test_retranslate_omits_unset_temperature() -> None:
    class Recording(FakeResponses):
        async def parse(self, **kwargs: dict) -> SimpleNamespace:
            self.kwargs = kwargs
            return await super().parse(**kwargs)

    completions = Recording()
    translator = _translator({}, completions)
    translator.temperature = None
    await translator.retranslate("hello", source=Lang.EN, target=Lang.DE)
    assert "temperature" not in completions.kwargs

    translator.temperature = 0.3
    await translator.retranslate("hello", source=Lang.EN, target=Lang.DE)
    assert completions.kwargs["temperature"] == 0.3  # noqa: PLR2004


@pytest.mark.asyncio
async def test_summarize_returns_trimmed_brief_and_tracks_usage() -> None:
    responses = FakeResponses()
    translator = _translator({}, responses)

    summary = await translator.summarize(_request(3))

    assert summary == "Ann is the boss."
    assert responses.script == "0|line 0\n1|line 1\n2|line 2"
    assert translator.usage == Usage(prompt_tokens=100, completion_tokens=20)


def test_story_brief_is_sent_only_when_a_summary_is_set() -> None:
    translator = OpenAiTranslator(model="test-model", openapi_key="key", cache={})
    request = _request(1)

    def payload(request: TranslationRequest) -> dict:
        completion = translator.get_completion(list(request.segments), request)
        return json.loads(completion["input"][1]["content"])

    assert "story_brief" not in payload(request)
    assert payload(replace(request, summary="Ann is the boss."))["story_brief"] == (
        "Ann is the boss."
    )


class MemoryStore:
    def __init__(self, data: dict[str, str] | None = None) -> None:
        self.data = data or {}

    async def get(self, key: str) -> str | None:
        return self.data.get(key)

    async def put(self, key: str, summary: str) -> None:
        self.data[key] = summary


def _recognized(key: str | None = "tv:house:s01e01") -> TranslationRequest:
    return replace(_request(2), metadata=TitleMetadata("House", "Pilot", key=key))


@pytest.mark.asyncio
async def test_summary_is_generated_on_a_miss_and_stored() -> None:
    responses = FakeResponses()
    store = MemoryStore()

    request, status = await add_summary(_recognized(), _translator({}, responses), store)

    assert status == SummaryStatus.GENERATED
    assert request.summary == "Ann is the boss."
    assert store.data == {"tv:house:s01e01": "Ann is the boss."}
    assert responses.calls == 1


@pytest.mark.asyncio
async def test_stored_summary_is_reused_without_a_model_call() -> None:
    responses = FakeResponses()
    store = MemoryStore({"tv:house:s01e01": "stored brief"})

    request, status = await add_summary(_recognized(), _translator({}, responses), store)

    assert status == SummaryStatus.STORED
    assert request.summary == "stored brief"
    assert responses.calls == 0


@pytest.mark.asyncio
async def test_unrecognized_media_is_not_summarized() -> None:
    responses = FakeResponses()

    for original in (_request(2), _recognized(key=None)):
        request, status = await add_summary(original, _translator({}, responses), MemoryStore())
        assert request is original
        assert status == SummaryStatus.SKIPPED

    assert responses.calls == 0


@pytest.mark.asyncio
async def test_summary_works_without_a_store() -> None:
    request, _ = await add_summary(_recognized(), _translator({}, FakeResponses()), None)

    assert request.summary == "Ann is the boss."


@pytest.mark.asyncio
async def test_summarizer_failure_is_swallowed() -> None:
    class Failing(FakeResponses):
        async def parse(self, **kwargs: dict) -> SimpleNamespace:
            if kwargs["text_format"] is OpenAiSummary:
                msg = "boom"
                raise RuntimeError(msg)
            return await super().parse(**kwargs)

    original = _recognized()
    store = MemoryStore()

    request, status = await add_summary(original, _translator({}, Failing()), store)

    assert status == SummaryStatus.FAILED
    assert request is original
    assert store.data == {}


def test_usage_subtraction() -> None:
    assert Usage(300, 60) - Usage(100, 20) == Usage(200, 40)

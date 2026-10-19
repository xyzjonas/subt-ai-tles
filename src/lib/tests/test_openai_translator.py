from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from subtaitles import Lang, OpenAiTranslator, ProgressData, Segment, TranslationRequest


def _completion(content: dict) -> SimpleNamespace:
    message = SimpleNamespace(content=json.dumps(content))
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeCompletions:
    """Echoes every requested item upper-cased, like a well-behaved model."""

    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **kwargs: dict) -> SimpleNamespace:
        self.calls += 1
        payload = json.loads(kwargs["messages"][1]["content"])
        if "variants" in payload:
            variants = [{"label": v["label"], "text": payload["text"].upper()} for v in payload["variants"]]
            return _completion({"variants": variants})
        items = [{"id": i["id"], "text": i["text"].upper()} for i in payload["items"]]
        return _completion({"translations": items})


def _translator(cache: dict, completions: FakeCompletions) -> OpenAiTranslator:
    translator = OpenAiTranslator(model="test-model", openapi_key="key", cache=cache)
    translator.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))  # type: ignore[assignment]
    return translator


def _request(count: int) -> TranslationRequest:
    segments = tuple(Segment(index=i, text=f"line {i}") for i in range(count))
    return TranslationRequest(segments=segments, source=Lang.EN, target=Lang.DE)


@pytest.mark.asyncio
async def test_progress_counts_segments_not_batches() -> None:
    translator = _translator({}, FakeCompletions())
    progress = ProgressData(total=0, current=0)

    response = await translator.translate(_request(70), progress)

    assert len(response) == 70
    assert progress.total == 70
    assert progress.current == 70  # three batches (30 + 30 + 10), counted in segments


@pytest.mark.asyncio
async def test_progress_includes_cached_segments() -> None:
    cache: dict = {}
    request = _request(40)
    await _translator(cache, FakeCompletions()).translate(request)

    completions = FakeCompletions()
    progress = ProgressData(total=0, current=0)
    await _translator(cache, completions).translate(request, progress)

    assert completions.calls == 0
    assert progress.current == progress.total == 40


@pytest.mark.asyncio
async def test_cached_segments_work_without_progress_object() -> None:
    cache: dict = {}
    request = _request(5)
    await _translator(cache, FakeCompletions()).translate(request)

    response = await _translator(cache, FakeCompletions()).translate(request, None)

    assert [s.translation for s in response] == [f"LINE {i}" for i in range(5)]


def test_organization_is_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_ORG_ID", raising=False)

    OpenAiTranslator(model="test-model", openapi_key="key", cache={})


@pytest.mark.asyncio
async def test_retranslate_returns_default_variants() -> None:
    translator = _translator({}, FakeCompletions())

    variants = await translator.retranslate("hello", source=Lang.EN, target=Lang.DE)

    assert [v.label for v in variants] == list(OpenAiTranslator.VARIANT_STYLES)
    assert all(v.text == "HELLO" for v in variants)


@pytest.mark.asyncio
async def test_retranslate_with_prompt_returns_single_custom_variant() -> None:
    translator = _translator({}, FakeCompletions())

    variants = await translator.retranslate(
        "hello", source=Lang.EN, target=Lang.DE, prompt="sound like a pirate"
    )

    assert [v.label for v in variants] == ["Custom"]

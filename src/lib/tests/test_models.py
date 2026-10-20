from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pysrt
import pytest
from subtaitles import Engine, Lang
from subtaitles.models import (
    Segment,
    TranslatedSegment,
    TranslationResponse,
)
from subtaitles.translate import translate_srt

from tests.utils import MockedTranslator

if TYPE_CHECKING:
    from pathlib import Path

NUM_SEGMENTS = 3


def _seg(index: int, text: str) -> Segment:
    return Segment(index=index, text=text)


def test_duplicate_text_segments_coexist() -> None:
    """Segments with identical text but different indices are distinct in dicts/sets."""
    a = _seg(0, "Yes.")
    b = _seg(1, "Yes.")
    c = _seg(2, "- No.")

    by_index = {s.index: s for s in (a, b, c)}
    assert len(by_index) == NUM_SEGMENTS
    assert by_index[0] is a
    assert by_index[1] is b
    assert by_index[2] is c


def test_cache_key_separates_by_language() -> None:
    seg = _seg(0, "Hello world")
    key_en_de = seg.cache_key(Lang.DE, "gpt-4")
    key_en_fr = seg.cache_key(Lang.FR, "gpt-4")
    key_en_de_other = seg.cache_key(Lang.DE, "gpt-3.5")
    assert key_en_de != key_en_fr
    assert key_en_de != key_en_de_other


def test_cache_key_separates_distinct_texts() -> None:
    """Segments with different text produce different cache keys."""
    seg_x = _seg(0, "First line")
    seg_y = _seg(0, "Second line")
    assert seg_x.cache_key(Lang.DE, "m") != seg_y.cache_key(Lang.DE, "m")


def test_translation_response_by_index() -> None:
    segs = (
        TranslatedSegment(index=0, source="a", translation="A", status="translated"),
        TranslatedSegment(index=2, source="c", translation="C", status="passthrough"),
        TranslatedSegment(index=1, source="b", translation="B", status="failed"),
    )
    resp = TranslationResponse(segments=segs, target=Lang.DE)
    by_idx = resp.by_index()
    assert by_idx[0].translation == "A"
    assert by_idx[1].translation == "B"
    assert by_idx[2].translation == "C"
    assert len(resp) == NUM_SEGMENTS


@pytest.mark.asyncio
async def test_round_trip_translate_srt(data: Path) -> None:
    """translate_srt reassembles subtitles correctly by index (no positional zip)."""
    srt_file = pysrt.open(data / "sub-short.srt")

    with mock.patch("subtaitles.translate.get_translator", return_value=MockedTranslator()):
        result = await translate_srt(srt_file, Lang.EN, Lang.EN, Engine.OPEN_AI)

    assert len(result) == len(srt_file)
    for original, translated in zip(srt_file, result, strict=True):
        assert translated.text == original.text
        assert translated.start == original.start
        assert translated.end == original.end

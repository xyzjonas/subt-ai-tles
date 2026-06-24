from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from datetime import timedelta

    from subtaitles.language import Lang


@dataclass(frozen=True, slots=True)
class Segment:
    index: int
    text: str
    raw: str | None = None
    start: timedelta | None = None
    end: timedelta | None = None
    speaker: str | None = None

    def cache_key(self, source: Lang, target: Lang, model: str) -> str:
        content = f"{self.text.strip().lower()}|{source}|{target}|{model}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class TranslationRequest:
    segments: Sequence[Segment]
    source: Lang
    target: Lang


@dataclass(frozen=True, slots=True)
class TranslatedSegment:
    index: int
    source: str
    translation: str
    status: Literal["translated", "passthrough", "failed"]


@dataclass(frozen=True)
class TranslationResponse:
    segments: tuple[TranslatedSegment, ...]
    source: Lang
    target: Lang

    def __iter__(self) -> Iterator[TranslatedSegment]:
        return iter(self.segments)

    def __len__(self) -> int:
        return len(self.segments)

    def by_index(self) -> dict[int, TranslatedSegment]:
        return {s.index: s for s in self.segments}

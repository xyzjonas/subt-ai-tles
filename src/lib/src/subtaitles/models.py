from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
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


@dataclass(frozen=True, slots=True)
class TitleMetadata:
    title: str
    description: str
    # stable identity of the recognized media (show + season + episode, or title + year)
    key: str | None = None


class SummaryStatus(StrEnum):
    """What happened to the story brief of a request."""

    GENERATED = "generated"
    STORED = "stored"
    SKIPPED = "skipped"  # media not recognized, nothing to key the brief on
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class TranslationVariant:
    label: str
    text: str


@dataclass(frozen=True)
class TranslationRequest:
    segments: Sequence[Segment]
    source: Lang
    target: Lang
    metadata: TitleMetadata | None = None
    # concise story brief (characters, plot, settings) shared with every batch
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class TranslatedSegment:
    index: int
    source: str
    translation: str
    status: Literal["translated", "passthrough", "failed"]


@dataclass(frozen=True, slots=True)
class Usage:
    """Tokens consumed by LLM calls."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            self.prompt_tokens + other.prompt_tokens,
            self.completion_tokens + other.completion_tokens,
        )

    def __sub__(self, other: Usage) -> Usage:
        return Usage(
            self.prompt_tokens - other.prompt_tokens,
            self.completion_tokens - other.completion_tokens,
        )


@dataclass(frozen=True)
class TranslationResponse:
    segments: tuple[TranslatedSegment, ...]
    source: Lang
    target: Lang
    usage: Usage = Usage()
    model: str | None = None

    def __iter__(self) -> Iterator[TranslatedSegment]:
        return iter(self.segments)

    def __len__(self) -> int:
        return len(self.segments)

    def by_index(self) -> dict[int, TranslatedSegment]:
        return {s.index: s for s in self.segments}


@dataclass(frozen=True, slots=True)
class RetranslationResponse:
    variants: list[TranslationVariant]
    usage: Usage = Usage()
    model: str | None = None

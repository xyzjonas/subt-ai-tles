# 000 — Core domain model (Segment / Request / Response)

**Priority:** Foundational — implement first · **Fixes:** the flat-type root cause behind 001–006 · **Area:** `providers/protocol.py`, `providers/openai.py`, `translate.py`, `cache.py`, exports

## Problem

The translation contract is `list[str] -> list[str]`
(`providers/protocol.py:14-21`):

```python
async def translate(
    self, text: list[str], language_from: Lang, language_to: Lang,
    progress: Progress | None = None,
) -> list[str]: ...
```

Everything downstream inherits this flatness, and it is the root cause the other
feature requests keep working around:

- **Alignment is positional**, reconciled with `zip(srt, translations,
  strict=False)` (`translate.py:47`), which silently truncates on mismatch.
- **No per-line provenance** — impossible to say whether a given line was
  translated, passed through, or failed (needed by 002, 006).
- **No per-line metadata** — no place for speaker/timing/markup (needed by 003, 005).
- **Cache identity is broken** — keyed on the batch's first line only
  (`cache.py:15`, called with `text[0]`), so distinct batches collide.

The tool is usable as a PoC but hard to embed in other tooling because the types
carry no structure, context, or flexibility.

## Goals

- Replace flat `list[str]` I/O with structured, **immutable** domain objects.
- Make line identity explicit (stable index) and **decouple it from caching**.
- Provide an extensible home for metadata without locking the API again.
- Return a **wrapper object**, not a bare list, so output can grow (stats, usage,
  warnings) without breaking the signature.

## Design

### `Segment` — one subtitle line + what we know about it

Frozen/immutable. Identity is the `index`, **not** the text (subtitle lines
repeat — `"Yes."`, `"- No."`, names — so content-based identity would collapse
duplicates in any set/dict).

```python
from dataclasses import dataclass
from datetime import timedelta

@dataclass(frozen=True, slots=True)
class Segment:
    index: int                       # stable, contiguous (0..n-1), for reassembly
    text: str                        # source text to translate (markup-stripped)
    raw: str | None = None           # original text incl. <i> tags, lossless (see Markup)
    start: timedelta | None = None   # timing — enables context windows (003)
    end: timedelta | None = None
    speaker: str | None = None       # filled by glossary pre-pass (003); None for now

    def cache_key(self, source: "Lang", target: "Lang", model: str) -> str:
        """Derived cache key — NOT the object's identity."""
        ...  # hash of normalized text + source + target + model (+ prompt version)
```

- **Use a fresh internal `index`**, not pysrt's SRT sequence number (which isn't
  guaranteed contiguous/unique in malformed files). Keep the SRT index/timing as
  metadata for round-tripping if needed.
- `cache_key()` is a **method**, deliberately separate from `__hash__`. Dedup of
  identical lines (translate once, fan out) becomes an explicit "group by
  cache_key" step, never an emergent side effect of object identity.

### `TranslationRequest` — binds segments to a direction

Language lives on the **job**, not on every line (it is identical for the whole
file; per-line duplication only invites inconsistency).

```python
from collections.abc import Sequence

@dataclass(frozen=True)
class TranslationRequest:
    segments: Sequence[Segment]      # Sequence, not Iterable — needs multiple passes
    source: Lang
    target: Lang
    # extension point: future options (glossary, context window, model override)
```

> Use `Sequence`, never a bare `Iterable`: batching, reassembly, and retries each
> traverse the segments more than once, so a one-shot generator would be unsafe.

### `TranslatedSegment` + `TranslationResponse` — the result

A **new** object per line (no mutation of the input `Segment`), and the provider
returns a **wrapper**, not `list[TranslatedSegment]`, so we never lock the return
type again.

```python
from typing import Literal

@dataclass(frozen=True, slots=True)
class TranslatedSegment:
    index: int                       # matches the source Segment.index
    source: str
    translation: str
    status: Literal["translated", "passthrough", "failed"]

@dataclass(frozen=True)
class TranslationResponse:
    segments: tuple[TranslatedSegment, ...]
    source: Lang
    target: Lang
    # extension point: token usage / cost, warnings, timing — addable later

    def __iter__(self): return iter(self.segments)
    def __len__(self): return len(self.segments)
    def by_index(self) -> dict[int, TranslatedSegment]:
        return {s.index: s for s in self.segments}
    # convenience for 002/006 reporting, e.g. counts grouped by status
```

- `status` is first-class provenance: `passthrough` is what 002's fallback ladder
  sets when it keeps the source; `failed`/`passthrough` is what 006 reports. "Did
  this line actually translate?" becomes a fact, not a guess.

### Protocol

```python
class TranslateProtocol(Protocol):
    async def translate(
        self, request: TranslationRequest, progress: Progress | None = None,
    ) -> TranslationResponse: ...
```

## Markup handling (honest scope)

General inline-tag reapplication is **not reliably doable** — translation
reorders words, so `<i>`/`<b>` offsets don't survive. Therefore:

- `Segment.raw` preserves the original text losslessly (cheap, optional).
- Default reassembly **drops inline markup**, exactly as today (`srt.py`).
- The one case worth doing now (high confidence): **whole-line wrap** — if the
  entire source line is wrapped in a single tag (`<i>…</i>`), re-wrap the
  translation. Safe because there's no offset mapping involved.
- General inline reapplication is explicitly **deferred to
  [005](005-misc-robustness-fixes.md)**. The foundation just refuses to lose the
  data.

If even the whole-line-wrap case is unwanted, dropping markup entirely is an
acceptable starting point — `raw` keeps the door open.

## Migration / impact

- `providers/protocol.py` — new protocol signature + new types (new module, e.g.
  `subtaitles/models.py`).
- `providers/openai.py` — consume `TranslationRequest`, build `TranslationResponse`;
  batch over `request.segments`, reassemble by `index`. Pairs naturally with
  structured output ([001](001-structured-output-alignment.md)).
- `translate.py` — build `Segment`s from the parsed `SubRipFile` (index, stripped
  `text`, `raw`, timing), call the translator, reassemble the `SubRipFile` from
  the response **by index** (drop `zip(strict=False)`).
- `cache.py` — replace first-line key with `Segment.cache_key(...)`.
- Update exports in `__init__.py`; update or delete the disabled providers
  (`libretranslate.py`, `pyd_ai.py`) to match the new signature.
- `task.py` / `cli.py` — largely unaffected (operate at file level).
- **Breaking API change** — bump version; update README usage.

## Sequencing

Land this **before** 001–006; it is the substrate they all build on:

- 001 (structured output) maps directly onto `Segment.index` ↔ response by index.
- 002 (fallback) uses `status` for `passthrough`/`failed`.
- 003 (context/glossary) uses `speaker`/timing and `TranslationRequest` options.
- 005 (markup) builds on `Segment.raw`.
- 006 (untranslated detection) sets `status` and reports via `TranslationResponse`.

## Acceptance criteria

- [ ] `translate` accepts a `TranslationRequest` and returns a
      `TranslationResponse`; no public `list[str] -> list[str]` path remains.
- [ ] `Segment` is frozen; its identity is `index`, and duplicate-text lines
      coexist without collapsing in sets/dicts.
- [ ] Caching uses a derived key (text + languages + model), not object identity
      or first-line-only; distinct batches with equal first lines cache separately.
- [ ] Reassembly is by `index`; no reliance on `zip(strict=False)` to hide
      mismatches.
- [ ] Output is a wrapper object that can gain fields without breaking callers.
- [ ] `raw` preserves original markup; reassembly drops inline markup (whole-line
      wrap optionally reapplied), with general handling deferred to 005.
- [ ] Disabled providers and exports updated to the new signature; version bumped.
- [ ] Tests cover round-tripping (build → translate → reassemble), duplicate-text
      segments, and cache-key separation.

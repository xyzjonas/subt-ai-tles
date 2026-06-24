# Feature Requests — Translation Robustness & Quality

These feature requests address two recurring user-facing problems:

1. **Lost nuance** — subtle distinctions (he/she forms, formal/informal address,
   tone, character consistency) are frequently lost in translation.
2. **Dropped / failed phrases** — the crude delimiter-based validation and
   all-or-nothing retry logic can blank out lines or fail an entire file.
3. **Silently untranslated output** — the model sometimes echoes the source
   text; it is structurally valid so nothing detects it.

Both share a root cause: the tool discards structure and context, then tries to
rebuild line alignment from a fragile text delimiter (`---`).

## Suggested implementation order

**[000](000-core-domain-model.md) is the foundation — implement it first.** It
replaces the flat `list[str] -> list[str]` contract with structured `Segment` /
`TranslationRequest` / `TranslationResponse` objects, which is the root cause the
rest of these keep working around. Each of 001–006 becomes clean (rather than a
workaround) once it exists.

| # | Feature | Fixes | Priority |
|---|---------|-------|----------|
| [000](000-core-domain-model.md) | Core domain model (Segment / Request / Response) | Foundation for all below | **First** |
| [001](001-structured-output-alignment.md) | Structured output for guaranteed line alignment | Dropped/failed phrases | **High** |
| [002](002-graceful-degradation-fallback.md) | Graceful degradation instead of all-or-nothing | Dropped/failed phrases | **High** |
| [003](003-translation-context-and-glossary.md) | Conversational context + character/glossary pre-pass | Lost nuance | **High** |
| [004](004-batching-and-model-tier.md) | Larger batches + configurable model tier | Both | Medium |
| [005](005-misc-robustness-fixes.md) | Cache key, markup preservation, retry variation | Both | Medium |
| [006](006-detect-untranslated-output.md) | Detect untranslated (still-source-language) output | Silently untranslated output | **High** |

Recommended grouping: land **000** first (foundation), then ship
**001 + 002 + 006** together (robustness — 006 reuses 002's fallback ladder),
then **003** (quality), then **004 + 005** as polish.

## Key files (current state)

- `src/subtaitles/providers/openai.py` — prompt building, API call, validation, retries
- `src/subtaitles/translate.py` — orchestration, SRT reconstruction
- `src/subtaitles/srt.py` — markup stripping
- `src/subtaitles/cache.py` — disk cache + cache-key construction
- `src/subtaitles/environment.py` — env-var configuration (model default)

# 005 — Cache key, markup preservation, retry variation

**Priority:** Medium · **Fixes:** both nuance and robustness · **Area:** `cache.py`, `srt.py`, `providers/openai.py`

A collection of smaller, independent fixes.

## A. Robust cache key

**Problem** — the cache key uses only the batch's first line
(`src/subtaitles/cache.py`):

```python
def get_cache_key(text: str, lang_from: Lang, lang_to: Lang) -> str:
    return f"{text}-{lang_from}-{lang_to}"
```

Called with `text[0]` (`providers/openai.py:81`). Two batches starting with the
same line (e.g. `"- Yeah."`) **collide** and return the wrong translation. The
key also doesn't change when the model changes, so stale results survive a model
upgrade.

**Fix** — hash the **full batch content + language pair + model (+ prompt
version)** into the key, e.g. a SHA-256 of the joined batch text plus
`lang_from`, `lang_to`, `model`. Invalidate naturally on any of those changing.

**Acceptance:** distinct batches with identical first lines cache separately;
changing the model produces fresh translations.

## B. Preserve / re-apply markup

**Problem** — `src/subtaitles/srt.py` strips `<i>`, `<b>`, etc. before
translation and never restores them:

```python
srt_markup_patterns = [re.compile(r"<.*?>")]
```

Emphasis (which sometimes carries meaning) and styling are lost in the output.

**Fix** — either (a) instruct the model to preserve inline tags and translate
around them, or (b) extract tag positions before translation and re-apply them
afterward. Option (a) is simpler and pairs well with structured output
([001](001-structured-output-alignment.md)); (b) is more robust if the model
mangles tags.

**Acceptance:** a line like `<i>Really?</i>` keeps its emphasis in the
translated output.

## C. Retry variation (if text-delimiter path is kept anywhere)

**Problem** — retries re-send a byte-identical, deterministic request
(`providers/openai.py:94-96, 102-105`), so they tend to reproduce the same
failure.

**Fix** — on retry, add a corrective message describing the mismatch and/or vary
temperature. (Largely superseded by [001](001-structured-output-alignment.md) +
[002](002-graceful-degradation-fallback.md), but worth doing wherever retries
remain.)

**Acceptance:** retried requests differ from the original; transient
mismatches resolve without exhausting all retries.

## D. Minor logging clarity (optional)

`MIN_RETRIES_TO_LOG = 3` (`providers/openai.py:23`) only logs the **last 3**
attempts (`if retries_left < MIN_RETRIES_TO_LOG`). Consider logging the first
failure too, so intermittent issues are visible without waiting for near-exhaustion.

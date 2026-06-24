# 002 — Graceful degradation instead of all-or-nothing

**Priority:** High · **Fixes:** dropped/failed phrases · **Area:** `providers/openai.py`, `translate.py`

## Problem

When a batch can't be reconciled after retries, the failure cascades to the
entire file — a 2-hour movie produces **no output** because of one stubborn
batch of 10 lines.

Current relevant code:

```python
# providers/openai.py:101-107
if len(res) != len(text):
    if retries_left > 0:
        return await self.process_batch(text, language_from, language_to, retries_left - 1)
    msg = f"Input lines count doesn't match output's line count! {text} --> {res}"
    raise ValueError(msg)
```

```python
# translate.py:85-88 — any ValueError fails the whole file
except ValueError as exc:
    raise FailedToTranslateError(path, new_path, f"Translator failed: {exc}") from exc
```

### Why it's too crude

1. **All-or-nothing:** one bad batch kills the entire film's output.
2. **Identical, deterministic retries:** re-sending the same request reproduces
   the same failure — retries mostly burn quota.

## Proposed solution

Introduce a **fallback ladder** so a batch degrades gracefully instead of failing:

1. **Batch attempt** (normal path, ideally with [001](001-structured-output-alignment.md)).
2. **Corrective retry:** if reconciliation fails, retry with a corrective
   message ("you returned N items, I need exactly M, one per id") and/or a
   varied temperature so the retry actually differs.
3. **Line-by-line fallback:** if the batch still won't reconcile, translate its
   lines individually (batch size 1). A single line cannot misalign.
4. **Passthrough last resort:** if an individual line still fails, keep the
   **original source text** for that one line and log a warning. A viewer
   prefers one untranslated line over a missing/blank one or a dead file.

### Implementation notes

- Add a config flag for strictness, e.g. `FAIL_ON_UNTRANSLATED` (default
  `False`) so power users can opt into hard failure if they prefer.
- Track and report how many lines fell back (per-line vs passthrough) — surface
  a summary count to the CLI/progress and logs.
- Reserve `FailedToTranslateError` for genuinely unrecoverable situations
  (e.g. auth/network errors, empty model responses), not single-line mismatches.
- Ensure the fallback respects the cache (cache successful line-level results too).

## Acceptance criteria

- [ ] A batch that fails reconciliation degrades to line-by-line translation
      rather than failing the file.
- [ ] A single irrecoverable line falls back to original text and the file still
      writes successfully.
- [ ] Retries differ from the original request (corrective message and/or
      temperature variation), not byte-identical re-sends.
- [ ] CLI/log output reports the count of fallback/passthrough lines.
- [ ] Optional strict mode (`FAIL_ON_UNTRANSLATED`) still raises when enabled.
- [ ] Tests cover: batch-level fallback, line-level fallback, and passthrough.

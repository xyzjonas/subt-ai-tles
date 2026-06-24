# 006 — Detect untranslated (still-source-language) output

**Priority:** High · **Fixes:** silent passthrough / echoed source text · **Area:** `providers/openai.py`, new validation module

## Problem

Sometimes the model returns the **source text unchanged** — the output stays in
the source language. This is the most dangerous failure mode because the result
is *structurally valid*: line counts match, delimiters are fine, nothing in the
current validation (`providers/openai.py:100-107`) inspects the **content**, so
it passes silently and ships untranslated subtitles.

### Why it happens

- **Weak models echo input.** `gpt-5-nano` (current default) sometimes copies the
  source verbatim — common on short lines, content it deems "already correct," or
  near a soft refusal.
- **Passthrough fallback** (see [002](002-graceful-degradation-fallback.md))
  intentionally keeps source text on irrecoverable lines; that path is logged,
  but a silent model-echo is not.
- Nothing currently checks whether output is actually in the target language.

## Proposed solution

A **dependency-free identity check with length-based gating**, decided at
aggregate granularity. The dominant failure mode is the model echoing the source
**verbatim**, which an identity check catches exactly — no language-detection
library required.

Key insight: for **longer** lines, an exact `source == target` match is almost
never legitimate (a full sentence identical in both languages essentially always
means it wasn't translated). False positives — `"OK"`, `"Hmm"`, names, numbers —
cluster in **short** lines, which the length gate excludes; the aggregate
threshold mops up any stragglers.

### The check

1. **Normalize** both source and translated text: strip surrounding whitespace,
   lowercase, optionally strip trailing punctuation/quotes.
2. **Exclude ineligible lines** from the check:
   - fewer than ~3 words / below a short character length, and
   - numeric- or symbol-only lines.
3. **Flag** each eligible line where normalized `translated == source`.
4. **Aggregate verdict (most reliable):** if the flagged fraction of *eligible*
   lines in a batch/file exceeds a threshold, treat that batch/file as
   untranslated. Aggregating avoids acting on a single noisy line.

### Known trade-off

This catches **verbatim echo** (the common case). It does NOT catch "reworded but
still in the source language" output — that is rarer and would need language
detection. Accepted as the cost of zero dependencies; language detection can be
added later as an optional enhancement if that case proves common (e.g. an
optional `lingua-py` backend behind the same interface).

### Wiring it in

- Treat "batch detected as source language" as a **reconciliation failure** that
  triggers the [002](002-graceful-degradation-fallback.md) fallback ladder
  (corrective retry → line-by-line → passthrough), rather than shipping silently.
- Surface a **whole-file guard**: after assembly, if the share of untranslated
  content exceeds a threshold, warn loudly (and optionally fail under
  `FAIL_ON_UNTRANSLATED`).
- Report counts to CLI/logs: how many lines were flagged untranslated and how
  many survived after fallback.

### Prevention (reduces frequency, complements detection)

- Stronger model tier (see [004](004-batching-and-model-tier.md)).
- Structured output (see [001](001-structured-output-alignment.md)) reduces
  echo-the-input behavior.
- Explicit instruction that output MUST be in the target language even if the
  source looks already translated.

## Implementation notes

- **No new dependencies** — pure-stdlib string normalization and comparison.
- Make the check toggleable via env (e.g. `DETECT_UNTRANSLATED`, default `True`).
- Thresholds (min words/length per line, aggregate fraction) should be config
  constants with sensible defaults.
- Source and target can share tokens (names, loanwords) — tune the aggregate
  threshold rather than expecting 0% identical matches.
- Keep the check behind a small interface so an optional language-detection
  backend can be slotted in later without touching call sites.

## Acceptance criteria

- [ ] A batch the model echoes back in the source language is detected and routed
      to the fallback ladder instead of shipping untranslated.
- [ ] Short lines, numbers, and proper nouns do not trigger false positives
      (excluded by the length gate / absorbed by the aggregate threshold).
- [ ] A whole-file guard warns (and optionally fails) when the untranslated share
      exceeds a threshold.
- [ ] CLI/logs report the count of flagged-untranslated and recovered lines.
- [ ] Detection is toggleable and thresholds are configurable.
- [ ] No new runtime dependencies are added.
- [ ] Tests cover: fully-echoed batch, partially-echoed batch, and a clean
      translation with legitimate proper-noun matches (no false positive).

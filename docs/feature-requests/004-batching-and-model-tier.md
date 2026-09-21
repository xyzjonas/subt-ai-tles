# 004 — Larger batches + configurable model tier

**Priority:** Medium · **Fixes:** both nuance and robustness · **Area:** `providers/openai.py`, `environment.py`

## Problem

- Batch size is fixed at **10** (`providers/openai.py:39`), which fragments
  context and provides little material for cross-line consistency.
- The default model is **`gpt-5-nano`** (`environment.py` default) — the weakest
  tier, and nuance is exactly what it's worst at.

```python
# providers/openai.py:39
batch_size: int = (10,)
```

## Proposed solution

- Once alignment is structural (see
  [001](001-structured-output-alignment.md)), larger batches become safe.
  Increase the default (e.g. 20–40 lines) to give the model more in-context
  dialogue and improve consistency.
- Make batch size configurable via env/CLI.
- Allow an easy model-tier override and document the quality/cost trade-off.
  Recommend `gpt-5-mini` (or higher) for quality-sensitive runs; keep `nano` as
  the budget floor.

### Implementation notes

- Larger batches increase per-request token usage and the blast radius of a
  single failed batch — this depends on [002](002-graceful-degradation-fallback.md)
  being in place so a large batch degrades gracefully.
- Consider token-aware batching (split on approximate token budget) rather than a
  fixed line count, so very long lines don't blow the context.
- Keep the default conservative; expose tuning for power users.

## Acceptance criteria

- [ ] Batch size is configurable; default raised once 001 + 002 are in place.
- [ ] Model is easily overridable via env/CLI with documented options.
- [ ] README documents the cost/quality trade-off of batch size and model tier.
- [ ] No increase in dropped lines at larger batch sizes (relies on 001 + 002).

# 001 — Structured output for guaranteed line alignment

**Priority:** High · **Fixes:** dropped/failed phrases · **Area:** `providers/openai.py`

## Problem

Line alignment between input and output is reconstructed from a fragile text
delimiter, and this is the single largest source of dropped phrases and
whole-file failures.

Current relevant code (`src/subtaitles/providers/openai.py`):

```python
# line 67 — items joined by a text delimiter
({"role": "user", "content": "---".join(items)},)

# line 100 — output split back on the delimiter, empty segments dropped
res = [line for line in response.choices[0].message.content.split(DELIMITER) if line]

# line 101 — count mismatch forces retry, eventually raises
if len(res) != len(text):
    ...
```

### Why it breaks

1. **`if line` silently drops empty translations**, guaranteeing a count
   mismatch even when the translation was otherwise correct.
2. **The delimiter `---` collides with real subtitle content.** Subtitles are
   full of dashes: dialogue dashes (`- Yes.` / `- No.`), em-dashes, trailing
   `--`. A `---` in the source or model output shatters the split.
3. **Relies on prompt compliance** ("KEEP the delimiters", "number of lines
   equal") rather than a structural guarantee.

## Proposed solution

Replace delimiter joining/splitting with **structured I/O** keyed by a stable id.

- Send each batch as numbered items, e.g. a JSON array:
  `[{"id": 0, "text": "..."}, {"id": 1, "text": "..."}]`.
- Request a structured response using OpenAI **structured outputs / JSON schema**
  (`response_format` with a strict schema) so the model must return one object
  per id.
- Reassemble by `id`, not by position or delimiter. Empty/blank translations
  become legal values rather than dropped segments.

### Implementation notes

- Define a response schema requiring an array of `{id: int, text: str}` with the
  same length as the input, `additionalProperties: false`, all fields required.
- Map results back into a list ordered by the original input index. If an id is
  missing, that is a *per-line* problem handed to the fallback logic (see
  [002](002-graceful-degradation-fallback.md)) rather than a whole-batch failure.
- Remove the `DELIMITER` constant and the `"---".join` / `.split(DELIMITER)` logic.
- Keep the system prompt's translation guidance; drop all
  delimiter-bookkeeping instructions ("KEEP the delimiters", "can't start/end
  with a delimiter", "number of lines equal").
- Confirm the configured model supports structured outputs; if not, document a
  JSON-mode fallback with explicit parse-and-validate.

## Acceptance criteria

- [ ] Subtitles containing `-`, `--`, `---`, and em-dashes translate without
      triggering count-mismatch retries.
- [ ] A line that legitimately translates to an empty/very short string is
      preserved (not dropped).
- [ ] Output list length always equals input length, or the discrepancy is
      surfaced per-line to the fallback path (never silently truncated).
- [ ] `zip(...)` in `translate.py:47` no longer relies on `strict=False` to hide
      length mismatches (set `strict=True` or guarantee equal length upstream).
- [ ] Existing tests pass; add tests for dash-heavy and empty-translation cases.

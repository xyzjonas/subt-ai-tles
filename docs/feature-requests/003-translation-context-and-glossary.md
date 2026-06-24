# 003 — Conversational context + character/glossary pre-pass

**Priority:** High · **Fixes:** lost nuance (he/she forms, formality, tone) · **Area:** `providers/openai.py`, `translate.py`

## Problem

Nuance is lost because the model translates isolated fragments with no idea who
is speaking, to whom, or what was said before.

Current relevant code (`src/subtaitles/providers/openai.py`):

```python
# line 67 — each batch is just 10 isolated lines, no surrounding dialogue
{"role": "user", "content": "---".join(items)},
```

Batches also run **independently and concurrently** (`translate.py` →
`asyncio.gather`), so consistency cannot carry across batches.

### Why nuance is lost

- **No context window:** gendered pronouns, formal/informal address (e.g. German
  *du/Sie*), and gendered adjective endings depend on *who is talking to whom* —
  invisible to a 10-line slice.
- **No cross-batch consistency:** if batch 3 infers a character is female, batch
  4 doesn't know. Names, address forms, and pronouns drift across the film.

## Proposed solution

Two complementary mechanisms (implement either or both; the glossary pre-pass
has the largest quality impact):

### A. Sliding-context window

- Include the previous N lines (and optionally the next N) as **read-only
  context** the model must *not* re-translate — clearly fenced (e.g. a
  `previous_context` field or a labeled block) so only the target batch lines are
  returned.
- Pairs naturally with the structured I/O from
  [001](001-structured-output-alignment.md).

### B. Character / glossary pre-pass

- Run one cheap first pass over the whole script (or a sample) to extract a
  **character sheet**: character names, inferred gender, relationships, and
  register/formality between speakers, plus a consistent translation for
  recurring terms/names.
- Inject this sheet into every batch's system prompt so all batches share the
  same ground truth → consistent pronouns and address forms film-wide.
- Cache the sheet per file so it's computed once.

### Implementation notes

- The glossary pre-pass can use structured outputs too (array of
  `{name, gender, formality, notes}`).
- Keep the sheet compact to limit token cost; it goes into every request.
- Make context size and the pre-pass toggleable via config/env (e.g.
  `CONTEXT_WINDOW`, `ENABLE_GLOSSARY`), since both add token cost.
- Because batches stop being fully independent, document the
  cost/latency/consistency trade-off (the pre-pass is sequential before fan-out).

## Acceptance criteria

- [ ] A character's pronouns/address form remain consistent across batches in a
      sample film known to currently drift.
- [ ] Gendered forms are preserved when the source/context makes gender clear.
- [ ] Context lines are used for grounding but never duplicated into the output.
- [ ] Glossary is computed once per file and reused (cached).
- [ ] Context window and glossary are toggleable and default to sensible values.

# DTM-213: Stage 21 M5 minimal read-model builder

## Context
- M5 needs concrete read-model generation from normalized tasks.
- Existing builder was a placeholder and could not produce consumer views.

## Goal
- Implement minimal read-model builder that emits:
  - `view_by_tasks`
  - `view_by_designer`
  - summary counters
- Add unit tests for ordering and grouping behavior.

## Non-goals
- No publication/storage of read models in this task.
- No frontend API switch to this builder yet.

## Plan
1. Implement builder logic in `src/services/readmodels/builder.py`.
2. Add test coverage in `tests/services/test_readmodel_builder.py`.
3. Run full suite and smoke checks.

## Checklist (DoD)
- [x] Builder emits both views and summary.
- [x] Deterministic ordering in outputs.
- [x] Unit tests added and passing.

## Work log
- 2026-03-02: Replaced builder placeholder with minimal v1 payload logic.
- 2026-03-02: Added read-model builder unit tests.
- 2026-03-02: Full tests and smoke checks stayed green.

## Links
- `src/services/readmodels/builder.py`
- `tests/services/test_readmodel_builder.py`

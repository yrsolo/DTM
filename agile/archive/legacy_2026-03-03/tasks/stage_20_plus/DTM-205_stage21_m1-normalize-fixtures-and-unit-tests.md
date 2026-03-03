# DTM-205: Stage 21 M1 normalize fixtures and unit tests

## Context
- M1 requires concrete fixture coverage and unit tests for normalize contracts.
- Repo had no active test scaffold for new `src/core/normalize` path.

## Goal
- Add fixture payloads for typical and edge cases (`dd.mm`, year boundary, invalid date token).
- Add unit tests for:
  - stage splitting
  - date inference
  - normalize interface

## Non-goals
- No runtime wiring to current production flow.
- No adapter/store integration changes.

## Plan
1. Add fixture JSON under `tests/fixtures/normalize`.
2. Add unit tests in `tests/core/normalize`.
3. Ensure `unittest discover` works in current repo.

## Checklist (DoD)
- [x] Fixtures committed.
- [x] Tests for parser/date/interface committed.
- [x] Tests executed and green.

## Work log
- 2026-03-02: Added fixture file `tests/fixtures/normalize/task_raw_samples.json`.
- 2026-03-02: Added 8 tests across stage parser, date inference, normalize interface.
- 2026-03-02: Added `__init__.py` in test folders so `unittest discover` finds nested tests.
- 2026-03-02: Executed `python -m unittest discover -s tests -p "test_*.py" -v` (8 passed).

## Links
- `tests/fixtures/normalize/task_raw_samples.json`
- `tests/core/normalize/test_stage_parser.py`
- `tests/core/normalize/test_date_inference.py`
- `tests/core/normalize/test_normalize_interface.py`

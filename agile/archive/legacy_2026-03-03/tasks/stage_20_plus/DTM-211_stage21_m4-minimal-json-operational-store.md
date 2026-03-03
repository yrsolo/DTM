# DTM-211: Stage 21 M4 minimal JSON operational store

## Context
- M4 requires operational store upsert contour before real YDB wiring.
- Need safe local/store-neutral implementation to continue migration incrementally.

## Goal
- Implement JSON-backed operational store adapter with upsert by `task_id`.
- Add idempotency unit test for upsert behavior.

## Non-goals
- No YDB SDK integration in this task.
- No runtime switch to store-backed read path yet.

## Plan
1. Replace placeholder `store_ydb` module with `JsonOperationalStore`.
2. Add adapter unit test for upsert idempotency.
3. Run full test/smoke suite.

## Checklist (DoD)
- [x] JSON adapter implemented.
- [x] Upsert idempotency test added.
- [x] Full tests and smoke checks pass.

## Work log
- 2026-03-02: Implemented `JsonOperationalStore` with `load/save/upsert_tasks`.
- 2026-03-02: Added `tests/adapters/test_json_store_adapter.py`.

## Links
- `src/adapters/store_ydb.py`
- `tests/adapters/test_json_store_adapter.py`

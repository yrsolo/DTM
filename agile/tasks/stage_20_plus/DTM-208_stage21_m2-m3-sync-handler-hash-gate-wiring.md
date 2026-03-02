# DTM-208: Stage 21 M2-M3 sync handler hash-gate wiring

## Context
- New architecture path needs a runnable handler boundary for sync orchestration.
- Hash-gate logic exists in service layer; handler wiring is needed for M2 split readiness.

## Goal
- Replace placeholder `src/handlers/sync.py` with working hash-gated handler.
- Add unit test that proves `first run -> execute`, `second unchanged run -> skip`.

## Non-goals
- No switch of production entrypoint to this handler.
- No source adapter integration yet.

## Plan
1. Wire `handle_sync` to `SyncService`.
2. Support optional event fields (`source_payload`, `source_id`, `state_file`).
3. Add tests for skip behavior.

## Checklist (DoD)
- [x] Handler returns structured sync decision payload.
- [x] Unit test for run/skip behavior added.
- [x] Test suite stays green.

## Work log
- 2026-03-02: Updated `src/handlers/sync.py` to call `SyncService`.
- 2026-03-02: Added `tests/handlers/test_sync_handler.py` with temp state file scenario.

## Links
- `src/handlers/sync.py`
- `tests/handlers/test_sync_handler.py`

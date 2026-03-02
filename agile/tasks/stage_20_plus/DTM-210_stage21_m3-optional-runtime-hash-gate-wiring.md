# DTM-210: Stage 21 M3 optional runtime hash-gate wiring

## Context
- Hash gate exists in new service layer, but current runtime flow had no optional wiring point.
- Need safe adoption path without changing default production behavior.

## Goal
- Wire source hash gate into `main.py` behind feature flag.
- Pass `allow_sync` switch into use-case so sync path can be skipped when unchanged.
- Keep reminders behavior intact for non-sync branches.

## Non-goals
- No default activation in production (`MIGRATION_ENABLE_SOURCE_HASH_GATE=0`).
- No replacement of legacy entrypoint architecture in this task.

## Plan
1. Add runtime flag/state path constants.
2. Compute hash basis from current repository task snapshot.
3. Evaluate gate and optionally skip sync branch.
4. Add unit tests for use-case `allow_sync` behavior.

## Checklist (DoD)
- [x] Hash-gate runtime wiring added behind flag.
- [x] Sync branch skip path implemented.
- [x] Unit tests for `allow_sync` branch switch added.
- [x] Smoke/test suite green.

## Work log
- 2026-03-02: Added migration hash-gate state path env var and config constant.
- 2026-03-02: Updated `main.py` to evaluate source hash gate and pass `allow_sync`.
- 2026-03-02: Updated `core/use_cases.py` to support sync skip path.
- 2026-03-02: Added `tests/core/test_use_cases.py`.

## Links
- `main.py`
- `core/use_cases.py`
- `config/constants.py`
- `src/services/sync/hash_gate.py`
- `tests/core/test_use_cases.py`

# DTM-206: Stage 21 M2-M3 feature flags and hash-gate smoke

## Context
- Need safe switch points before wiring new architecture path into runtime.
- Need executable proof that source hash gate behavior works (run -> skip unchanged).

## Goal
- Add migration feature flags with safe defaults (`0`).
- Add independent smoke script for hash-gate decision cycle.

## Non-goals
- No activation of new sync/render path in production runtime.
- No integration wiring into current cloud handlers yet.

## Plan
1. Add migration flags to config constants and `.env.example`.
2. Add hash-gate smoke script under `agent/`.
3. Run smoke and compile checks.

## Checklist (DoD)
- [x] Migration flags added to config and environment template.
- [x] Hash-gate smoke script committed.
- [x] Smoke script passed (first run executes, second run skips).

## Work log
- 2026-03-02: Added `MIGRATION_ENABLE_NEW_SYNC_PATH`, `MIGRATION_ENABLE_NEW_RENDER_PATH`, `MIGRATION_ENABLE_SOURCE_HASH_GATE`, `MIGRATION_DUAL_WRITE_STORE`.
- 2026-03-02: Added `agent/sync_hash_gate_smoke.py`.
- 2026-03-02: Executed `python agent/sync_hash_gate_smoke.py` (hash gate behaved as expected).

## Links
- `config/constants.py`
- `.env.example`
- `agent/sync_hash_gate_smoke.py`

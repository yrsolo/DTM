# DTM-232: Stage 22 tri-block smoke suite from unified query source

## Context
- Stage 22 requires runnable parity evidence across API, render, and notify blocks from one query contract.
- After DTM-229/DTM-230, shared query adapter and source-policy matrix are active.

## Goal
- Add deterministic tri-block smoke script proving parity on one fixture set.
- Add unit test for smoke snapshot expectations.

## Non-goals
- No cloud deploy or contour switch in this task.
- No API contract/schema change.

## Plan
1. Add smoke script with one shared fixture set for API/render/notify paths.
2. Add unit test for snapshot parity.
3. Run smoke + unit checks and capture evidence.

## Checklist (DoD)
- [x] `agent/stage22_tri_block_smoke.py` added.
- [x] `tests/services/test_stage22_tri_block_smoke.py` added.
- [x] README updated with Stage 22 smoke command.
- [x] Smoke script and tests passed.

## Work log
- 2026-03-03: Implemented tri-block smoke script with shared fixtures and parity assertions.
- 2026-03-03: Added unit test for smoke snapshot parity.
- 2026-03-03: Updated README with smoke command reference.
- 2026-03-03: Validation passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.services.test_stage22_tri_block_smoke tests.services.test_source_policy tests.test_task_query_contract -v`
  - `.venv\\Scripts\\python.exe agent\\stage22_tri_block_smoke.py`

## Links
- Smoke script: `agent/stage22_tri_block_smoke.py`

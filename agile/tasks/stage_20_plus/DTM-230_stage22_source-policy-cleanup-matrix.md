# DTM-230: Source-policy cleanup matrix for API/render/notify

## Context
- Stage 22 requires one explicit source-policy matrix across three product blocks.
- Source-switch conditions were duplicated in `main.py` and `index.py`.

## Goal
- Introduce one shared source-policy module.
- Rewire runtime entrypoints to the shared policy matrix.
- Keep runtime behavior unchanged.

## Non-goals
- No change to rollout values in `.env`.
- No API contract changes.

## Plan
1. Create shared source-policy matrix module.
2. Rewire `main.py` render/notify source switching to matrix methods.
3. Rewire `index.py` API source switching to matrix methods.
4. Add matrix unit tests and run timer smoke.

## Checklist (DoD)
- [x] Shared matrix module added (`src/services/source_policy.py`).
- [x] `main.py` switched to matrix-based render/notify source checks.
- [x] `index.py` switched to matrix-based API source checks.
- [x] Unit tests passed (`test_source_policy`, `test_main_source_switch`, `test_frontend_api_routing`).
- [x] `run_timer.cmd` passed.

## Work log
- 2026-03-03: Added `SourcePolicyMatrix` and builders in `src/services/source_policy.py`.
- 2026-03-03: Switched `main._apply_task_source_switches` to policy matrix calls.
- 2026-03-03: Switched API source checks in `index.py` to policy matrix calls.
- 2026-03-03: Validation passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.services.test_source_policy tests.core.test_main_source_switch tests.api.test_frontend_api_routing -v`
  - `cmd /c run_timer.cmd`

## Links
- Stage 22 plan: `doc/stages/68_stage22_execution_plan.md`

# DTM-229: Unified DB query contract adapter for API/render/notify

## Context
- Stage 22 objective requires one shared query contract and one filter semantics across three product blocks.
- Filtering/projection logic existed in `core/task_query_contract.py`, but consumers still had duplicated projection/query entry points.

## Goal
- Introduce one reusable adapter layer for projection + query operations.
- Rewire API payload builders, planner render path, and reminder selection path to that adapter.
- Keep runtime behavior unchanged.

## Non-goals
- No contract version bump.
- No rollout switch changes.

## Plan
1. Add shared adapter module over query contract.
2. Switch API v1/v2 payload builders to adapter.
3. Switch planner/reminder query entry points to adapter.
4. Run unit tests and timer smoke.

## Checklist (DoD)
- [x] `core/task_query_adapter.py` added with reusable context + query helpers.
- [x] API v1/v2 payload builders moved to adapter entry points.
- [x] Planner/reminder query paths moved to adapter entry points.
- [x] Query/routing/api v2 tests passed.
- [x] `run_timer.cmd` passed.

## Work log
- 2026-03-03: Added `TaskQueryContext` adapter in `core/task_query_adapter.py`.
- 2026-03-03: Rewired consumers:
  - `core/api_payload.py`
  - `core/api_payload_v2.py`
  - `core/planner.py`
  - `core/reminder.py`
- 2026-03-03: Validation passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_task_query_contract tests.api.test_frontend_api_v2_payload tests.api.test_frontend_api_routing -v`
  - `cmd /c run_timer.cmd`

## Links
- Stage 22 plan: `doc/stages/68_stage22_execution_plan.md`

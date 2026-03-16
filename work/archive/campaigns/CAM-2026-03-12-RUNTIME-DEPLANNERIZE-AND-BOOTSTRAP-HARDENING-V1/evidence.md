# Evidence - CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1

## Trust gate
- source: owner-provided reference bundle, verified active runtime code
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `agent/intructions/DTM-test/work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md`
  - `index.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
- trust_level: medium
- notes:
  - imported brief is accepted as campaign intent only
  - active code must remain the execution truth for concrete refactor decisions

## Verified baseline findings
- `index.py` creates `APP_CONTEXT = build_app_context()` at import time
- `src/entrypoints/runtime/planner_runtime_entry.py` creates global runtime context at import time
- current runtime still treats planner runtime as an active orchestration center

## Execution evidence
- 2026-03-12: `index.py` moved runtime bootstrap behind `_get_app_context()` / `_get_dispatcher()` lazy boundaries; no module-level `AppContext` construction remains
- 2026-03-12: `src/entrypoints/runtime/planner_runtime_entry.py` now accepts optional `app_context` via `PlannerRuntimeRequest` and builds context only inside `run_planner_runtime()`
- 2026-03-12: `src/entrypoints/http/runtime_execution.py` now forwards the already-built HTTP app context into planner runtime requests instead of forcing a second bootstrap path
- 2026-03-12: compatibility surface preserved via lazy `index.APP_DEPS` / `index.APP_TRIGGERS` proxies, so old tests can still mutate runtime deps without reintroducing import-time side effects
- 2026-03-12: import smoke passed via `python -m unittest tests.entrypoints.test_import_safety`
- 2026-03-12: compatibility smoke passed via `python -m unittest tests.api.test_runtime_execution tests.api.test_command_queue_foundation tests.api.test_frontend_api_routing`

## After state
- `index.py` imports safely under stripped env and exposes `handler` without calling `build_app_context()` on module import
- `src/entrypoints/runtime/planner_runtime_entry.py` imports safely under stripped env and exposes `run_planner_runtime` without calling `build_app_context()` on module import
- `build_app_context()` remains only at explicit runtime/factory boundaries:
  - `index._get_app_context()`
  - `run_planner_runtime(request)` when no `request.app_context` is supplied
- active planner runtime callers still exist (`runtime_shell.py`, `local_runtime.py`, `src/legacy/main.py`), but planner runtime is now a transitional adapter and no longer a module-import bootstrap center

## Required evidence during execution
- before/after import smoke for `index.py`
- before/after import smoke for `planner_runtime_entry.py`
- before/after import-smoke outputs
- code pointers for removed module-level bootstrap
- code pointers showing no module-level context construction
- list of active call paths no longer planner-centric

## Risks
- hidden env coupling may exist outside the obvious runtime entry modules
- bootstrap cleanup may expose more transitional imports

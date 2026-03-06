# CAM-LEGACY-PLANNER-DELETE-V1.evidence

## Trust gate
- source: `src/entrypoints/runtime/planner_runtime_entry.py`, `src/entrypoints/http/group_query_tasks_loader.py`, `src/services/planner_runtime.py`, `src/app/planner_bootstrap.py`, `src/entrypoints/jobs/planner_setup_job.py`
- last_verified_at: 2026-03-06
- verified_by: Codex agent
- trust_level: high
- evidence:
  - runtime grep for planner imports/usages:
    - `GoogleSheetPlanner`
    - `build_planner_dependencies`
    - `build_planner_runtime`
    - `run_planner_use_case`

## Runtime map (P01-T001)
- **HTTP/entrypoints:**
  - `index.py` and `main.py` call shared `run_planner_runtime`.
  - `src/entrypoints/runtime/planner_runtime_entry.py` still contains legacy planner branch under:
    - `mode.startswith("legacy_planner_")`
    - legacy default modes when `store_mode` is legacy (`timer/test/morning`)
- **Jobs/helpers:**
  - `src/entrypoints/jobs/planner_setup_job.py` builds planner runtime through bootstrap.
  - `src/entrypoints/jobs/source_switch_job.py` performs repo source switching for planner graph.
- **Services:**
  - `src/services/planner_runtime.py` hosts `GoogleSheetPlanner`.
  - `src/services/usecases/planner_runtime.py` executes legacy planner update/reminder flow.
- **HTTP group-query path:**
  - `src/entrypoints/http/group_query_tasks_loader.py` still calls `build_planner_dependencies(...)` directly.

## Current blockers for full cutover
1. Standard legacy `timer/test/morning` branch still enters planner when `store_mode=legacy`.
2. Group-query handler still uses legacy text parser/formatter wrappers (`src.legacy.http_core_bindings`), even though planner dependency is removed.

## Next safe migration slice
1. Replace `src.legacy.http_core_bindings` in group-query handler with dedicated snapshot-native parser/formatter.
2. Restrict planner branch to explicit `legacy_planner_*` modes only.

## Progress update (P02-T001)
- `src/entrypoints/http/group_query_tasks_loader.py` no longer imports planner bootstrap.
- Active-task loading in helper now reads from snapshot engine via frontend query adapter.


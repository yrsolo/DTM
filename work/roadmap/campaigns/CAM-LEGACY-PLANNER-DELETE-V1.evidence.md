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
1. Planner modules/files are still located in active namespace (`src/services/planner_runtime.py`, `src/app/planner_bootstrap.py`) and not yet quarantined to dedicated legacy namespace.

## Next safe migration slice
1. Move/quarantine remaining planner modules to explicit legacy namespace.
2. Remove planner-specific config knobs from default non-legacy path.

## Progress update (P02-T001)
- `src/entrypoints/http/group_query_tasks_loader.py` no longer imports planner bootstrap.
- Active-task loading in helper now reads from snapshot engine via frontend query adapter.
- `src/entrypoints/http/group_query_handler.py` no longer imports `src.legacy.http_core_bindings`; parser/formatter logic moved local to snapshot-based handler.

## Progress update (P03-T001)
- `src/entrypoints/runtime/planner_runtime_entry.py` now enables planner branch only for `legacy_planner_*` modes.
- Standard modes are routed through modern contours:
  - `timer/test/sync-only` -> `TimerPipeline` (snapshot update)
  - `morning/reminders-only/reminder_v2` -> notify v2 path
  - `timer/test/render_v2` -> render v2 path


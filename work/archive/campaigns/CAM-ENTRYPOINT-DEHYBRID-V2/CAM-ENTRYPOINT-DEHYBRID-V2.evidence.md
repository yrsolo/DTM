# CAM-ENTRYPOINT-DEHYBRID-V2 Evidence

## Trust Gate
- source: `index.py`, `main.py`, `src/entrypoints/http/*`, `src/entrypoints/jobs/*`
- last_verified_at: 2026-03-04
- verified_by: codex
- evidence: grep/runtime scan performed on active branch
- trust_level: high
- notes: campaign activated after STRAIGHTEN-V2 archive.

## Execution Log
- 2026-03-04: verified `index.py` has no `import main` and no `main.main` call.
- 2026-03-04: verified `main.py` is thin wrapper over `run_planner_runtime`.
- 2026-03-04: removed legacy planner fallback from `src/entrypoints/http/frontend_v2_handler.py`.
  - API v2 now serves only readmodel snapshot path.
  - on readmodel transport failure returns structured `503 frontend_source_unavailable` with `source=readmodel`.
- 2026-03-04: simplified HTTP dispatch wiring (`src/entrypoints/http/http_dispatch_chain.py`, `index.py`) by removing v2 legacy fallback dependencies.
- 2026-03-04: group-query flow remains isolated in dedicated handler (`src/entrypoints/http/group_query_handler.py`) and separate task loader.
- 2026-03-04: timer path assessment:
  - `planner_runtime_entry` still initializes planner dependencies for standard timer flow.
  - next safe extraction step is moving planner-only assembly behind explicit legacy mode while preserving current timer behavior.
- 2026-03-04: owner decision received: redesign timer path now.
- 2026-03-04: implemented TaskSource-based timer path:
  - added `src/services/sources/task_source.py`
  - added `src/services/sources/sheets_normalized_source.py`
  - `src/services/pipeline_runtime.py` now reads preflight/full snapshot from task source and builds tasks only after full fetch is required.
  - `src/entrypoints/runtime/planner_runtime_entry.py` standard path uses `build_sheets_normalized_task_source(...)`.
  - planner wiring is isolated behind explicit `mode=legacy_planner_*` lazy branch.
- 2026-03-04: tests passed.
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v`
  - `python -m unittest tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v`

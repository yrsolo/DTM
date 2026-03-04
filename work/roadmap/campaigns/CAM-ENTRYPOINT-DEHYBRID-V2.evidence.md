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
- 2026-03-04: blocker raised for P03-T002 (owner decision required on timer-path redesign scope).
  - owner notification sent via `python agent/notify_owner.py --mode blocked ...`.
- 2026-03-04: tests passed.
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v`
  - `python -m unittest tests.services.test_pipeline_runtime tests.services.test_sync_source_hash_gate -v`

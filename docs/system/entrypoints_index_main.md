# Entrypoints Behavior (Current): `index.py` and `main.py`

This file reflects current runtime behavior after dehybrid and pipeline-straighten changes.

## `main.py`

`main.py` is a thin async wrapper:
- imports `run_planner_runtime` from `src/entrypoints/runtime/planner_runtime_entry.py`
- exposes `main(**kwargs)` that directly delegates to `run_planner_runtime(**kwargs)`
- has no orchestration logic of its own

## Shared runtime entry: `src/entrypoints/runtime/planner_runtime_entry.py`

This is the canonical runtime path used by both jobs and HTTP-triggered planner modes.

Flow:
1. Resolve mode/context with `resolve_runtime_context(...)`.
2. Handle `db_migrate` via `run_db_migrate_if_requested(...)`.
3. Build planner runtime via `build_planner_runtime(...)`.
4. Probe readmodel freshness marker via `run_readmodel_freshness_probe(...)`.
5. Run planner pipeline via `run_planner_pipeline(...)`.

Important behavior:
- There is no legacy file-state hash gate in runtime.
- Sync allow/skip decisions are made only inside canonical sync path (`YdbSyncService`).
- Preflight-first pipeline can skip full snapshot fetch when unchanged.

## `index.py`

`index.py` is an HTTP/runtime shell:
- parses incoming event
- dispatches HTTP routes via `src/entrypoints/http/*`
- runs group-query flow via HTTP handlers and explicit legacy bindings namespace (`src/legacy/http_core_bindings.py`)
- for planner modes delegates to `execute_runtime(main_func=run_planner_runtime, ...)`

Key constraints now satisfied:
- `index.py` does not import or call `main.main`
- `index.py` has no direct `core.*` imports

## API behavior

- Primary contract: API v2 (`/api/v2/frontend` and docs endpoints).
- Legacy-source failure on v2 path returns structured `503 frontend_source_unavailable`, with emergency YDB fallback path when available.
- HTTP runtime has dispatch error boundary returning structured `503 http_dispatch_failed` instead of raw gateway failure.

## Why this doc exists

`index.py` and runtime entry modules are high-churn boundaries. This file is the current behavior reference used for trust checks in campaign work.

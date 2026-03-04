# Entrypoints Behavior (Current): `index.py` and `main.py`

This file reflects current runtime behavior after dehybrid, straighten, and wrapper-dto changes.

## `main.py`

`main.py` is a thin async wrapper:
- imports `PlannerRuntimeRequest` and `run_planner_runtime` from `src/entrypoints/runtime/planner_runtime_entry.py`
- exposes `main(request=None, *, event, mode, dry_run, mock_external, force_refresh)`
- builds `PlannerRuntimeRequest` (if needed) and delegates to `run_planner_runtime(request)`
- has no orchestration logic of its own

## Shared runtime entry: `src/entrypoints/runtime/planner_runtime_entry.py`

Canonical runtime path used by jobs and HTTP-triggered planner modes.

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
- for planner modes delegates to `execute_runtime(...)`, which constructs `PlannerRuntimeRequest` and calls `run_planner_runtime(request)`

Key constraints now satisfied:
- `index.py` does not import or call `main.main`
- `index.py` has no direct `core.*` imports

## API behavior

- Primary contract: API v2 (`/api/v2/frontend` and docs endpoints).
- Legacy-source failure on v2 path returns structured `503 frontend_source_unavailable`, with emergency YDB fallback path when available.
- HTTP runtime has dispatch error boundary returning structured `503 http_dispatch_failed` instead of raw gateway failure.

## Why this doc exists

`index.py` and runtime entry modules are high-churn boundaries. This file is the current behavior reference used for trust checks in campaign work.

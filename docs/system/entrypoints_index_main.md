# Entrypoints Behavior (Current): `index.py` and `main.py`

This file reflects runtime behavior after demonster refactor: class-based HTTP router/handlers and canonical timer pipeline object.

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
3. Build canonical Sheets task source via `build_sheets_normalized_task_source(...)`.
4. Optionally run legacy planner contour only for `mode=legacy_planner_*`.
5. Probe readmodel freshness marker via `run_readmodel_freshness_probe(...)`.
6. Run canonical timer pipeline via `TimerPipeline(APP_CONTEXT).run(TimerRunRequest(...))`.

Important behavior:
- There is no legacy file-state hash gate in runtime.
- Sync allow/skip decisions are made only inside canonical sync path (`YdbSyncService`).
- Preflight-first pipeline can skip full snapshot fetch when unchanged.
- Canonical sync module is `src/services/sync_service.py`.
- Standard timer mode does not import or execute `GoogleSheetPlanner` wiring.
- In `store_mode=legacy`, `mode=timer` keeps legacy render/update path, while `mode=sync-only` explicitly triggers canonical YDB sync + readmodel rebuild (safe API recovery path).

## `index.py`

`index.py` is an HTTP/runtime shell:
- parses incoming event into `HttpRequest`
- dispatches HTTP routes via `HttpRouter(ctx).dispatch(req)`
- router uses handler classes:
  - `GroupQueryHandler`
  - `FrontendRootHandler`
  - `FrontendV2Handler`
- for planner modes delegates to `RuntimeExecutor(ctx).execute(...)`, which builds `PlannerRuntimeRequest` and calls `run_planner_runtime(request)`

Key constraints now satisfied:
- `index.py` does not import or call `main.main`
- `index.py` has no direct `core.*` imports
- `index.py` has no functional context dataclasses and no lambda wiring

## API behavior

- Primary contract: API v2 (`/api/v2/frontend` and docs endpoints).
- API v2 reads frontend readmodel snapshot (YDB readmodel path, no planner rebuild in handler).
- Readmodel unavailability returns structured `503 frontend_source_unavailable` (`details.source=readmodel`).
- HTTP runtime has dispatch error boundary returning structured `503 http_dispatch_failed` instead of raw gateway failure.

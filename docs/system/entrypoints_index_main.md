# Entrypoints Behavior (Current): `index.py` and `main.py`

## `main.py`

`main.py` is a thin wrapper:
- builds `PlannerRuntimeRequest`
- delegates execution to `run_planner_runtime(...)`

No domain orchestration is implemented directly in `main.py`.

## Runtime entry: `src/entrypoints/runtime/planner_runtime_entry.py`

Canonical runtime flow:
1. resolve mode/context
2. build sheets task source
3. call `TimerPipeline(AppContext).run(...)`

Timer pipeline now updates snapshot engine storage (S3 raw/prep) and does not build/read YDB readmodel for API v2 runtime path.

## `index.py`

`index.py` is an HTTP/runtime shell:
- parse event -> `HttpRequest`
- dispatch via `HttpRouter(ctx).dispatch(req)`
- for non-HTTP runtime modes call runtime executor

`index.py` does not import `main.main` and has no lambda/factory wiring in runtime dispatch.

## HTTP handlers
- `FrontendRootHandler`: root/doc compatibility
- `FrontendV2Handler`: reads data from snapshot engine prep cache
- `GroupQueryHandler`: reads active snapshot-backed tasks and sends Telegram response

## API source-of-truth

For API v2 runtime:
- canonical source: S3 prep snapshot
- metadata marker: `meta.readmodelSource = "s3_snapshot"`

YDB readmodel is not used as primary source in this contour.

## Legacy Cut Roadmap (current)

Still legacy-backed runtime contours:
- render path in standard `timer/test` flow (planner branch).
- notify/reminder path for `morning/test/reminders-only` (planner reminder stack).

Already snapshot-engine backed:
- API v2 (`/api/v2/frontend`)
- group-query task source
- info panel (`/info`, `/api/v2/info`)

Planned campaign sequence:
1. `CAM-LEGACY-CUT-API-V1`
2. `CAM-NOTIFY-MODULE-V1`
3. `CAM-RENDER-MODULE-V1`
4. `CAM-HTTP-FALLBACK-REMOVAL-V1`
5. `CAM-LEGACY-PLANNER-DELETE-V1`

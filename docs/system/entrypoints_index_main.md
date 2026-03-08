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
- `TelegramWebhookHandler`: validates Telegram webhook secret, parses update, maps to internal command, and enqueues it
- `GroupQueryHandler`: compatibility wrapper aliasing Telegram webhook intake
- `AdminQueueHandler`: hidden admin enqueue/upload-contract endpoints for async mutations (`update_snapshot`, render, reminders, attachments)
- `InfoHandler`: operator dashboard for snapshot state, queue live state, build metadata, recent jobs, and render diagnostics

## API source-of-truth

For API v2 runtime:
- canonical source: S3 prep snapshot
- metadata marker: `meta.readmodelSource = "s3_snapshot"`

YDB readmodel is not used as primary source in this contour.

## Legacy Cut Roadmap (current)

Already snapshot-engine backed:
- API v2 (`/api/v2/frontend`)
- worker-side group-query reply job task source
- info panel (`/info`, `/api/v2/info`)
- standard runtime modes:
  - `timer/test/sync-only` via `TimerPipeline`
  - `morning/reminders-only/reminder_v2` via notify v2 path
  - `timer/test/render_v2` via render v2 path

Telegram intake policy:
- webhook path stays `/telegram`
- webhook validates `X-Telegram-Bot-Api-Secret-Token`
- webhook does not execute business selection/rendering inline
- webhook enqueues commands such as `group_query_reply`
- worker jobs perform the actual Telegram reply or admin action

Attachment mutation policy:
- upload contract is requested through hidden admin endpoint, not through API v2 read path
- binary upload goes directly to Object Storage
- worker-side `attach_task_file` command updates snapshot extra-store and rebuilds prep
- API v2 only exposes attachment metadata, not storage keys

Render v2 policy:
- target worksheet key: `task_calendar` (`Задачи`);
- forbidden worksheet key: `tasks` (`ТАБЛИЧКА`);
- if target is unsafe runtime returns structured blocked result with `render_target_unsafe`.

Info observability policy:
- `/info` stays synchronous and read-only
- it may call live Yandex APIs for queue depth and active function build metadata
- async admin actions report through queue-backed job status and recent-history blocks
- render RCA should use `jobs.latestByCommand.render_timeline_sheet` and `renderDebug`, not raw enqueue HTTP status

Planned campaign sequence:
1. `CAM-LEGACY-CUT-API-V1`
2. `CAM-NOTIFY-MODULE-V1`
3. `CAM-RENDER-MODULE-V1`
4. `CAM-HTTP-FALLBACK-REMOVAL-V1`
5. `CAM-LEGACY-PLANNER-DELETE-V1`

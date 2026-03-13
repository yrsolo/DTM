# Entrypoints Behavior (Current): `index.py` and standard runtime shells

## Archived local wrapper

`main.py` is no longer an active top-level entrypoint.

Current local runtime flow:
- `local_run.py`
- `src/entrypoints/runtime/local_runtime.py`
- `run_planner_runtime(...)`

Archived wrapper code now lives under:
- `src/legacy/main.py`

## Runtime entry: `src/entrypoints/runtime/planner_runtime_entry.py`

Canonical runtime flow:
1. resolve mode/context
2. build `AppContext` inside explicit runtime execution only
3. build sheets task source
4. call `TimerPipeline(AppContext).run(...)`

Timer pipeline now updates snapshot engine storage (S3 raw/prep) and does not build/read YDB readmodel for API v2 runtime path.

Standard runtime modes only:
- `timer`
- `sync-only`
- `render_v2`
- `reminder_v2`
- `reminders-only`
- `morning`
- `test`

Legacy planner modes are no longer supported in standard runtime and return explicit `unsupported_mode`.

## `index.py`

`index.py` is now a true thin shell:
- keep module import side-effect free
- lazily resolve `AppContext` and `IndexDispatcher` on first runtime access
- delegate `handler(event, ctx)` to dispatcher

Transport-specific branching lives outside `index.py`:
- `src/entrypoints/index_dispatcher.py`
- `src/entrypoints/event_classifier.py`
- `src/entrypoints/http/http_shell.py`
- `src/entrypoints/queue/worker_shell.py`
- `src/entrypoints/triggers/trigger_shell.py`
- `src/entrypoints/runtime/runtime_shell.py`

`index.py` no longer imports queue DTOs, HTTP parser helpers, runtime executors, YDB repo classes, or `planner_runtime_entry` directly.

## HTTP handlers
- `FrontendRootHandler`: root/doc compatibility
- `FrontendV2Handler`: reads data from snapshot engine prep cache
- `TelegramWebhookHandler`: validates Telegram webhook secret, parses update, maps to internal command, and enqueues it
- `GroupQueryHandler`: compatibility wrapper aliasing Telegram webhook intake
- `AdminQueueHandler`: hidden admin enqueue/upload-contract endpoints for async mutations (`update_snapshot`, render, reminders, trigger emulation, attachments)
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
- human-facing render timestamps and `today` anchor use configured runtime timezone (`runtime.timezone`, default `Europe/Moscow`).

Info observability policy:
- `/info` stays synchronous and read-only
- default `/info` and `/info?format=json` return lightweight summary payload only
- heavy diagnostics are exposed only through explicit detail mode (`/info/detail` or `view=detail`)
- it may call live Yandex APIs for queue depth and active function build metadata
- async admin actions report through queue-backed job status and recent-history blocks
- render RCA should use `jobs.latestByCommand.render_timeline_sheet` and `renderDebug`, not raw enqueue HTTP status
- `/info?format=json` keeps machine timestamps in UTC; HTML may show additive MSK display for operator convenience

Queue retry policy:
- queue-driven retry is the current model
- worker distinguishes `failed_retryable` vs `failed_terminal`
- worker shell returns non-success transport only when retry is requested
- canonical status vocabulary is documented in `docs/system/job_status_schema.md`

Telegram command routing policy:
- parser builds a typed `ParsedTelegramUpdate`
- `TelegramCommandRouter` maps typed updates to internal command intents
- webhook stays thin and enqueue-only
- group query must continue to reuse reminder selection path on worker side

Trigger queue policy:
- when queue mode is enabled, `timer` trigger does not execute runtime inline
- it enqueues three commands for the worker path:
  - `update_snapshot`
  - `render_timeline_sheet`
  - `render_designers_sheet`
- `morning` trigger remains enqueue-only and produces `send_reminders`

Legacy reference policy:
- archived compatibility helpers now live under `src/legacy/entrypoints/jobs/`
- standard runtime must not import `src.legacy.*` or old planner/store helpers
- guard script: `python scripts/check_no_legacy_entrypoint_imports.py`

Current state:
- legacy-cut sequence for standard entrypoints is completed
- archived planner/bootstrap/render/readmodel-probe code now lives under `src/legacy/`
- archived compat bootstrap/manager/use-case shims now also live under:
  - `src/legacy/core/`
  - `src/legacy/services/usecases/`
- any remaining legacy cleanup should target reference modules outside active runtime path

# Dataflow, Hashing, Versioning (Current)

Canonical path: Sheets -> normalize -> Raw snapshot (S3) -> Prep snapshot (S3) -> API v2/query consumers.

## 1) Snapshot inputs
Source snapshot is read from Sheets range `A1:Z2000` and includes:
- `values`
- `colors`

Hash basis is stable JSON over `{values, colors}`.

## 2) Canonical timer runtime
Runtime object:
- `src/services/timer_pipeline.py` -> `TimerPipeline(AppContext)`
- `TimerPipeline.run(RunRequest(...))` invokes `SnapshotEngine.update(...)`
- top-level transport dispatch: `index.py` -> `src/entrypoint/handler.py`
- runtime bridge for explicit modes: `src/entrypoints/runtime/runtime_shell.py`

Execution order:
1. fetch sheet snapshot
2. compute source hash
3. compare with previous raw snapshot hash
4. on change (or force): write Raw -> build Prep -> write Prep
5. on no-change: skip writes

No YDB operational/readmodel writes are part of the canonical API v2 runtime path.
No legacy planner/store/readmodel-probe branch is part of the canonical standard runtime path.

People routing snapshot:
- timer update also refreshes people snapshot from sheet `Люди` into S3.
- notify uses people snapshot as canonical source for `chat_id` and `vacation`.

Attachment metadata contour:
- binary payloads are uploaded directly to Object Storage under `attachments/{env}/{task_id}/...`
- admin upload-contract endpoint is `POST /ops/admin/task-attachments/request-upload`
- finalize endpoint is `POST /ops/admin/task-attachments/finalize`
- delete endpoint is `POST /ops/admin/task-attachments/delete`
- metadata attach/delete still execute asynchronously through queue jobs
- metadata is persisted in snapshot extra-store under canonical bulk key `snapshots/{env}/extra/default.json`
- runtime no longer reads per-task extra objects from the hot path
- worker commands `attach_task_file` and `delete_task_attachment` update extra-store and rebuild prep from current raw snapshot
- API v2 exposes attachment metadata through `tasks[].attachments` without exposing storage keys
- browser reads go through `/ops/api/task-attachments/{attachment_id}/{view|download}` with trusted/full access only

Prep-build hot path:
- load one bulk extra snapshot
- reconcile orphan flags in memory
- write bulk extra snapshot once only if orphan state changed
- build `tasks_by_id`
- build prep indexes

Prep timing metrics:
- `dtm.snapshot.extra_load_ms`
- `dtm.snapshot.orphan_reconcile_ms`
- `dtm.snapshot.task_view_build_ms`
- `dtm.snapshot.prep_index_build_ms`

## Render v2 safety and target policy
- `render_v2` reads only snapshot prep data.
- `render_v2` target worksheet is `task_calendar` (human name: `Задачи`).
- `render_v2` must never write to `tasks` (`ТАБЛИЧКА`) source sheet.
- Unsafe target is blocked at runtime with `error.code=render_target_unsafe`.

## 3) Query runtime
- API handler: `src/contexts/access_api/internal/frontend_v2_handler.py` via `src/entrypoints/http/router.py`
- Query engine: `src/contexts/snapshot/internal/engine/query_engine.py`
- Source: `PrepSnapshot` from S3

Payload contract remains API v2 compatible (including `history`, `brand`, `format_`, `customer`).

## 4) Status semantics
- `status`: normalized color-derived status (`work|pre_done|wait|done|unknown`)
- `history`: raw textual status from source sheet

## 5) Telegram group query/runtime
- webhook intake: `src/contexts/telegram_interaction/internal/webhook.py`
- parser: `src/contexts/telegram_interaction/internal/parser.py`
- worker job: `src/contexts/telegram_interaction/internal/job_runner.py`

Execution order:
1. receive Telegram webhook on `/telegram`
2. validate `X-Telegram-Bot-Api-Secret-Token`
3. parse update into internal command
4. enqueue `group_query_reply` (or safe admin command)
5. worker executes reminder-based selection and sends Telegram reply

No business selection or snapshot reads happen inline in webhook intake.

## 6) Reminder parity runtime
- reminder modes (`reminder_v2`, `reminders-only`, `morning`, `test`) use `src/contexts/reminders/internal/*` as the owning reminder contour.
- candidate designers are selected only from tasks with milestones on:
  - today,
  - next workday (weekend-aware).
- message flow:
  1) draft by formatter
  2) optional LLM enhancement
  3) fallback to draft on empty/error
  4) Telegram delivery with retries/backoff/classified counters
- in `env=test` all reminder sends are forced to test chat routing.

## 7) People registry note
- people snapshot keeps the full mapped `Люди` row contract, not only reminder fields.
- secret-only `GET /api/v2/people` may return the full registry snapshot for internal auth-support consumers.
- this registry is separate from `frontend_v2.entities.people`, which remains a derived owner list from selected tasks.
- people registry stores both:
  - `contact_email` -> `contactEmail`
  - `yandex_email` -> `yandexEmail`
- `attributes` stays inside snapshot storage as internal completeness layer and is intentionally not returned by `/api/v2/people`.
- `is_active` is derived during people snapshot refresh from explicit markers in `vacation` and `info`:
  - inactive vacation markers: `да`, `+`, `отпуск`
  - inactive info markers: `не работает`, `уволен`, explicit cross-mark symbols
  - `.` does not mark inactivity

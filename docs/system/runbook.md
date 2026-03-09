# Runbook (Current)

This is a minimal runbook to operate the current system.

## 1) Local setup
1) Create `.env.dev` (or copy from `.env.dev.example`).
2) Ensure Google credentials are available via one of:
   - `GOOGLE_KEY_JSON_PATH`
   - `GOOGLE_KEY_JSON_B64`
   - `GOOGLE_KEY_JSON`
3) For YDB access set (test/prod aware):
   - `YDB_ENDPOINT_TEST`, `YDB_DATABASE_TEST` (and/or PROD)
   - optionally `YDB_ID_TEST/PROD`

## 2) Create tables (one-time)
Option A (recommended): run migration mode with env flag:
- set `YDB_MIGRATE_ON_START=1` and run the migrate job through `local_run.py` / standard runtime mode.

Option B: call schema ensure via code path (dev only).

## 3) Timer update (Snapshot Engine)
Run job mode that performs:
- Sheets snapshot fetch (`values + colors`)
- normalize -> raw snapshot
- prep build (raw + extra merge)
- S3 write for raw/prep snapshots

Operational mode note:
- canonical API v2 data source is S3 prep snapshot.
- `mode=sync-only` remains the explicit manual rebuild mode.

Key safety knobs:
- `READMODEL_TTL_MINUTES` (default 9)
- `PREFLIGHT_TOP_ROWS` (default 50)
- `FULL_SYNC_INTERVAL_HOURS` (default 24)
- `FORCE_REFRESH=1` to force rebuild WITHOUT version bumps

## 4) API (frontend v2)
API reads prep snapshot from S3 via snapshot engine.

Health markers in response:
- `meta.readmodelSource = "s3_snapshot"`
- `meta.sourceHash`
- `meta.sourceId`

## 4.1) Reminder v2
Reminder runtime source:
- tasks from prep snapshot
- people routing from people snapshot (`snapshots/{env}/people/default.json`)

Reminder selection:
- designers are selected only by milestones on today and next workday.
- default statuses: `work`, `pre_done`.

Delivery safety:
- if `ENV=test`, sends are forced to test chat override.
- vacation `да` skips delivery.
- retry policy: 3 attempts with backoff and classified counters.

## 4.2) Telegram webhook intake
Telegram runtime policy:
- only webhook mode, no polling
- webhook path: `runtime.telegram.webhook_path` (current default `/telegram`)
- secret header required: `X-Telegram-Bot-Api-Secret-Token`
- webhook returns transport success quickly and enqueues command execution

Current supported enqueue mappings:
- group `/tasks` or mention -> `group_query_reply`
- group `/deadlines` or mention with deadline wording -> `group_query_reply`
- private `/update` from default chat -> `update_snapshot`
- private `/reminders_test` from default chat -> `send_reminders`

Ops visibility:
- `/info?format=json` includes `telegram.webhookPath`, `telegram.webhookUrl`, `telegram.allowedUpdates`, `telegram.maxConnections`, `telegram.secretConfigured`

## 4.4) `/info` operational dashboard
`/info` is the operator page for async runtime visibility.

Current observability sources:
- S3 snapshot meta and storage counters
- S3 job-status store:
  - latest by command
  - recent terminal jobs
  - recent failed jobs
- Yandex Message Queue live attributes
- Yandex Cloud Functions live build metadata

Key JSON blocks:
- `build`
- `queue.live`
- `jobs.recent`
- `jobs.failedRecent`
- `jobs.latestByCommand`
- `renderDebug`

## 4.3) Attachment metadata flow
Attachment upload/runtime policy:
- request upload contract through hidden admin endpoint `POST /admin/attachments/request-upload`
- upload binary directly to Object Storage with returned `PUT` URL
- enqueue metadata mutation through `POST /admin/commands/attach-task-file`
- worker updates extra-store and rebuilds prep from current raw snapshot

Current storage policy:
- binary key prefix: `attachments/{env}/{task_id}/{attachment_id}-{filename}`
- metadata source of truth: `snapshots/{env}/extra/{task_id}.json`
- API v2 exposes only attachment metadata (`id`, `filename`, `mime`, `size`, `uploadedAt`, `uploadedBy`, `preview`)
- storage `key` is not exposed in frontend API payload

## 5) Milestones invariants
Milestones must never be empty:
- sync adds `start` if missing
- builder synthesizes `start` if timing is empty in source

## 6) Troubleshooting
### Snapshot source unavailable
- check Object Storage credentials and bucket/prefix config:
  - `runtime.snapshot_engine.bucket`
  - `runtime.snapshot_engine.prefix_raw|prefix_prep|prefix_extra|prefix_people`
- startup should fail-fast if snapshot engine is enabled but required fields are empty.

### Missing milestones
If logs show synthetic `start`:
- timing payload in source task is empty or not parsed.
- verify source timing text and normalization logs.

### Render safety (incident prevention)
- `render_v2` is allowed to write only to worksheet `task_calendar` (`Задачи`).
- `render_v2` must never target `tasks` (`ТАБЛИЧКА`).
- On unsafe target runtime responds with `error.code=render_target_unsafe` and does not write.
- Before release verify source/target spreadsheet separation for prod contour.

### Render triage through `/info`
When `Force render table` appears to do nothing:
1. open `/info`
2. inspect `Queue State`
3. inspect `Last Render Job`
4. inspect `Render Debug`

Interpretation:
- queue visible > 0 and no terminal render job -> worker/trigger problem
- `renderDebug.state=blocked` -> target guard blocked write
- `renderDebug.state=failed` -> render job failed; inspect `error`
- `renderDebug.state=noop` -> render ran but had nothing to apply
- `renderDebug.state=applied` -> render reported success; verify target spreadsheet/worksheet

### Human-facing timezone policy
- human-facing render timestamps use `runtime.timezone` (current default `Europe/Moscow`)
- this affects the display timestamp in rendered Google Sheets (for example cell `A1`) and “today” anchor logic used by render selection/highlighting
- JSON/system timestamps remain UTC ISO for API and operator JSON payloads

## 7) Branching and test deploy
1) Development goes to `dev` (small commits, push to origin).
2) When test contour validation is needed, merge `dev` into `test`.
3) Push `test` to origin:
   - test deploy workflow starts automatically.
4) Production promotion stays owner-controlled: owner manually creates/reviews PR `test -> main`, then runs manual production release workflow.

## 8) Legacy-cut state
Current state:
- `index.py` is a thin shell delegating to `IndexDispatcher`
- `local_run.py` uses `src/entrypoints/runtime/local_runtime.py`; `main.py` is archived under `src/legacy/main.py`
- standard runtime no longer supports `legacy_planner_*`
- legacy planner/bootstrap/render/readmodel-probe/source-switch helpers are archived under `src/legacy/`
- legacy compat bootstrap/manager/use-case shims are also archived under `src/legacy/core/` and `src/legacy/services/usecases/`

## 9) Anti-relapse gate
Run import guard before merge to `test`:
- `python scripts/check_no_legacy_entrypoint_imports.py`

Target violations:
- `src.legacy` imports from active entrypoints/runtime
- `src.adapters.store_ydb`
- `src.entrypoints.jobs.legacy_store_write_job`
- `src.entrypoints.jobs.planner_pipeline_job`
- `src.entrypoints.jobs.planner_setup_job`
- `src.entrypoints.jobs.source_switch_job`
- `src.services.usecases.planner_runtime`
- `src.app.planner_bootstrap`
- `src.services.planner_runtime`
- `src.services.calendar_runtime`
- `src.services.render.task_table_runtime`
- `src.entrypoints.jobs.readmodel_probe_job`
- `src.entrypoints.jobs.readmodel_freshness`
- `core.bootstrap`
- `core.manager`
- `main`
- any import growth in `index.py` beyond `build_app_context` and `IndexDispatcher`

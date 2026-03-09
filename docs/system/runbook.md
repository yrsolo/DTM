# Runbook (Current)

This is the minimal operator/developer runbook for the current runtime.

## 1) Local setup
1. Create `.env.dev` or copy from `.env.dev.example`.
2. Ensure Google credentials are available via one of:
   - `GOOGLE_KEY_JSON_PATH`
   - `GOOGLE_KEY_JSON_B64`
   - `GOOGLE_KEY_JSON`
3. Ensure Object Storage credentials are available for snapshot/job-status paths.

## 2) Snapshot update
`mode=sync-only` is the explicit manual rebuild mode.

Current canonical flow:
- Sheets fetch
- normalize to raw snapshot
- merge extra -> prep snapshot
- write raw/prep snapshots to Object Storage

API v2 reads prep snapshot, not YDB readmodel.

## 3) Reminder v2
Reminder runtime source:
- tasks from prep snapshot
- people routing from people snapshot

Selection:
- today + next workday milestones
- default statuses: `work`, `pre_done`

Delivery safety:
- `ENV=test` forces test chat override
- vacation `да` skips delivery
- notifier keeps its own send retry logic for Telegram delivery

Queue/worker safety:
- command retry model is queue-driven
- retryable worker failures are stored as `failed_retryable`
- terminal worker failures are stored as `failed_terminal`

## 4) Telegram webhook intake
Policy:
- webhook only, no polling
- validate `X-Telegram-Bot-Api-Secret-Token`
- parse typed Telegram update
- route to internal command
- enqueue and return quickly

Current supported async mappings:
- group `/tasks` -> `group_query_reply`
- group `/deadlines` -> `group_query_reply`
- private `/update` from default admin chat -> `update_snapshot`
- private `/send_statuses` from default admin chat -> `send_reminders`
- private `/render_timeline` from default admin chat -> `render_timeline_sheet`

Routing rule:
- parser and router are separate concerns
- webhook does not execute business logic inline
- group query remains a worker-side operation using reminder selection semantics

## 5) `/info` operator dashboard
`/info` is the operational dashboard for async execution visibility.

Current sources:
- snapshot meta and storage counters
- job status store
- live queue attributes
- live function build metadata

Key JSON blocks:
- `build`
- `queue.live`
- `queue.policy`
- `jobs.recent`
- `jobs.failedRecent`
- `jobs.latestByCommand`
- `renderDebug`
- `telemetry`

Use `/info` first when diagnosing queue/render/reminder behavior.

## 6) Attachments metadata flow
Current policy:
- request upload contract via hidden admin endpoint
- upload binary directly to Object Storage
- enqueue `attach_task_file`
- worker updates extra-store and rebuilds prep from current raw snapshot

Frontend API exposes metadata only, not raw storage keys.

## 7) Render safety
- `render_v2` may write only to worksheet key `task_calendar` (`Задачи`)
- `render_v2` must never target `tasks` (`ТАБЛИЧКА`)
- unsafe target returns `render_target_unsafe` and performs no write
- human-facing render timestamps and `today` anchor use `runtime.timezone` (`Europe/Moscow` by default)
- machine-facing JSON timestamps remain UTC

## 8) Render triage through `/info`
When render appears to do nothing:
1. inspect `Queue State`
2. inspect `Last Render Job`
3. inspect `Render Debug`

Interpretation:
- queue backlog with no terminal render job -> worker/trigger issue
- `renderDebug.state=blocked` -> target guard blocked write
- `renderDebug.state=failed` -> render job failed
- `renderDebug.state=noop` -> render ran but had nothing to apply
- `renderDebug.state=applied` -> render reported success; verify target spreadsheet/worksheet

## 9) Branching and deploy
1. Development goes to `dev`.
2. Merge `dev -> test` for test contour validation.
3. Push `test` to trigger test deploy workflow.
4. Production release remains owner-controlled.

## 10) Legacy-cut state
Current state:
- `index.py` is a thin shell delegating to `IndexDispatcher`
- `local_run.py` uses `src/entrypoints/runtime/local_runtime.py`
- `main.py` is archived under `src/legacy/main.py`
- standard runtime no longer supports `legacy_planner_*`
- archived planner/bootstrap/render/readmodel-probe helpers live under `src/legacy/`

## 11) Anti-relapse gates
Run before merge to `test`:
- `python scripts/check_no_monsters.py`
- `python scripts/check_no_legacy_entrypoint_imports.py`
- `python scripts/check_no_legacy_imports.py`

These guard against:
- reintroducing legacy planner/runtime imports into active paths
- reintroducing `core/*`, `pandas`, `GoogleSheetPlanner`, `build_planner_dependencies`
- growing top-level shells back into monsters

## 12) Observability foundation
Shared abstractions:
- `src/observability/metrics.py`
- `src/observability/timing.py`
- `src/observability/logging.py`

Current defaults:
- metrics client: `NoopMetricsClient` locally unless monitoring is enabled
- structured logger: `StdoutJsonLogger`

This keeps instrumentation points stable before a full external metrics backend is enabled.

## 13) Yandex Monitoring integration
Current rollout policy:

- test-first
- real custom metrics backend on test
- prod remains disabled until explicit owner-approved rollout

Current operator checks:

1. open `/info?format=json`
2. inspect `telemetry` block:
   - `metricsEnabled`
   - `metricsClient`
   - `monitoringBackend`
   - `monitoringFolderId`
   - `dashboardName`
   - `dashboardId`
3. trigger:
   - API request
   - render
   - reminder
   - telegram accepted path
4. verify matching `dtm.*` metrics in Yandex Monitoring for `env=test`

If metrics are missing:

1. check monitoring enablement in deployed env
2. check resolved folder id
3. check service account Monitoring write rights
4. inspect logs for `monitoring_metric_emit_failed`
5. verify dashboard separately; dashboard automation is allowed to lag behind ingestion

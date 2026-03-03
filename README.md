# Designers Task Manager (DTM)

DTM is a real-world pet project built as a portfolio case about evolving legacy automation into a maintainable product architecture.

## What the project does
- Reads task data from Google Sheets.
- Builds visual planning views for a design team (timeline and designer-focused boards).
- Sends morning reminders to designers via Telegram.
- Responds in group chat when bot is mentioned/commanded with current tasks or nearest deadlines.
- Uses configurable LLM provider to improve reminder text style (`openai` / `google` / `yandex`), with automatic fallback to draft text when enhancer is unavailable.
- Reminder delivery has in-run duplicate guard (idempotent send key) to prevent repeated sends in one runtime cycle.
- Reminder text enhancement is processed in parallel with bounded concurrency for faster multi-designer runs.
- Reminder delivery now applies bounded retry/backoff for transient Telegram send failures.

## Why this repository exists
- Show practical refactoring of a working legacy system.
- Demonstrate safe migration approach: preserve business behavior while improving code quality.
- Build a foundation for moving from Google Sheets visualization to a dedicated frontend.

## Documentation entrypoint
- Start with `doc/00_documentation_map.md` for readable navigation and recommended read order.

## Architecture & Migration Plan
- Target architecture (layered, strangler migration):
  - `docs/architecture/target-architecture.md`
- Stage-by-stage migration plan (M1..M8):
  - `docs/migration/plan.md`
- Current Stage-21 DB finalization execution notes:
  - `docs/migration_plan.md`
- Atomic tasks by stage:
  - `docs/migration/tasks.md`
- YDB schema and DB rollout plan:
  - `docs/db/schema.md`
  - `docs/db/migration-plan.md`
  - `docs/evidence_db_migration_v2.md`
- Data contracts (raw/normalized/read-model):
  - `docs/contracts/data-contracts.md`
- Engineering standards:
  - `docs/standards/engineering-standards.md`

## Tech stack
- Python
- Google Sheets / Drive API
- Telegram Bot API
- OpenAI API
- Google Generative Language API (optional provider)
- Yandex Foundation Models API (optional provider)
- Yandex Cloud / Object Storage

## Engineering focus
- Separation of source and target sheets for safer testing.
- Local test contour for repeatable verification.
- Documentation-first reconstruction plan.
- Security hygiene for public repository readiness.

## Project status
- Test contour auto-deploy workflow is active on `main`.
- Production release workflow is manual (`workflow_dispatch`).
- Architecture is under phased reconstruction.
- Legacy snapshot is kept in `old/` for controlled comparison during migration.
- Stage 0-19 status and evidence index are tracked in `doc/03_reconstruction_backlog.md`.
- Current sprint/task execution state is tracked in `agile/sprint_current.md`.
- Serverless deploy setup (test/prod split) is in `doc/ops/stage9_main_autodeploy_setup.md`.
- Deployment smoke and rollback runbooks are in:
  - `doc/ops/stage9_deployment_smoke_checklist.md`
  - `doc/ops/stage10_function_rollback_drill.md`
  - `doc/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`
- Stage 8 prototype loader utility: `agent/load_prototype_payload.py` (filesystem/Object Storage + schema gate).
- Stage 8 static prototype assets: `web_prototype/static` (run local preview with `.venv\Scripts\python.exe agent\run_web_prototype_server.py`).
- Stage 8 payload preparation helper: `.venv\Scripts\python.exe agent\prepare_web_prototype_payload.py --source-mode auto` (writes `web_prototype/static/prototype_payload.json`).
- Stage 8 shadow-run evidence builder: `.venv\Scripts\python.exe agent\stage8_shadow_run_evidence.py` (builds execution evidence package under `artifacts/shadow_run_stage8`).
- Deploy run evidence report builder: `.venv\Scripts\python.exe agent\deploy_run_evidence_report.py --per-page 1 --output-file artifacts/tmp/deploy_run_evidence.json`.
- Main-branch test auto-deploy workflow: `.github/workflows/deploy_yc_function_main.yml`.
  - Includes contract smoke gate before deploy:
    - `python agent/read_model_contract_compat_smoke.py`
    - `python agent/schema_snapshot_smoke.py`
- Manual production release workflow: `.github/workflows/release_yc_function_prod.yml`.

### Migration checklist (current)
- [x] Legacy runtime is stable and deployed in test/prod contours.
- [x] API/read-model contract baseline exists for current frontend integration.
- [x] Migration documentation package added (`docs/architecture|migration|contracts|standards`).
- [x] M1-M3 scaffolding added under `src/` (core models/normalize + sync hash gate).
- [x] M1 normalize fixtures and unit tests added (`tests/core/normalize`, `tests/fixtures/normalize`).
- [x] M3 optional runtime source hash gate wiring added (feature-flagged).
- [x] M4 optional dual-write to JSON operational store added (feature-flagged).
- [x] Rollout switches introduced: `STORE_MODE`, `READMODEL_SOURCE`, optional `NOTIFY_SOURCE`/`RENDER_SOURCE`.
- [ ] M1 wired to current runtime path.
- [ ] M2 sync/render split wired to handlers.
- [ ] M3 source-hash gate enabled in production flow.

### Store rollout policy
- `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
- `READMODEL_SOURCE=legacy|ydb`
- Optional: `NOTIFY_SOURCE`, `RENDER_SOURCE` (`legacy|ydb`)
- Runtime sync gates:
  - `READMODEL_TTL_MINUTES` (default `9`)
  - `PREFLIGHT_TOP_ROWS` (default `50`)
  - `FULL_SYNC_INTERVAL_HOURS` (default `24`)
  - `FORCE_REFRESH=0|1` (forced full refresh without version bump for existing tasks)
- Prod order:
  1. `STORE_MODE=dual_write`
  2. switch readmodel/notify sources to `ydb`
  3. `STORE_MODE=ydb_primary`, then `STORE_MODE=ydb_only`

## Local run (current)
- Preferred: `run_timer.cmd` (uses project virtualenv and runs timer mode).
- Direct CLI: `.venv\Scripts\python.exe local_run.py --mode timer`
- Available run modes:
  - `timer`: sync pipeline only (legacy behavior).
  - `morning`: reminders only on weekdays (legacy behavior).
  - `test`: sync + reminders (legacy behavior).
  - `sync-only`: explicit sync-only run (no reminders).
  - `reminders-only`: explicit reminders-only run (no sheet sync path).
- Safe verification mode: add `--dry-run` to disable Google Sheets write operations while keeping read flow and dry-run logs.
- External side-effect guard for reminder tests: add `--mock-external` to disable OpenAI and Telegram calls in reminder flow.
- `mode=test` now enables mock external mode by default in `main.py` unless explicitly overridden.
- Optional artifact export: `--quality-report-file <path>` writes structured diagnostics snapshot (`task/people row issues`, `timing parse errors`) as JSON.
- Optional trend persistence: `--sli-trend-file <path>` appends rolling reminder SLI snapshots across runs (use `--sli-trend-limit <N>` to cap history length, default `200`).
- Optional Stage 6 artifact publication: `--read-model-file <path>` writes canonical read-model JSON from current run artifacts (`--read-model-build-id <id>` sets source build marker).
- Optional Stage 7 schema snapshot publication: `--schema-snapshot-file <path>` writes read-model schema snapshot JSON.
- Optional cloud export for schema snapshot: `--schema-snapshot-s3-key <key>` uploads schema snapshot to Object Storage (requires `S3_BUCKET` and S3 credentials envs).
- Reminder run summary now includes delivery counters (`sent`, `skipped_*`, `send_errors`) and quality report summary includes reminder send/error counts.
- Quality report summary also includes retry counters: `reminder_send_retry_attempt_count` and `reminder_send_retry_exhausted_count`.
- Quality report summary now also includes derived reminder SLI metrics: attemptable deliveries, attempted sends, delivery rate, and failure rate.
- Automated threshold evaluator (latest artifact auto-discovery):
  - `.venv\Scripts\python.exe agent\reminder_alert_evaluator.py --format text --fail-profile ci`
  - `run_alert_eval_ci.cmd` (CI wrapper command with `--fail-profile ci`)
- Local review wiring options:
  - `--evaluate-alerts` prints evaluator result from current run quality report.
  - `--alert-evaluation-file <path>` saves evaluator JSON artifact.
  - `--alert-fail-profile local|ci` controls preset exit policy (`local=none`, `ci=warn`).
  - `--alert-fail-on none|warn|critical` explicitly overrides preset exit policy.
  - `--notify-owner-on none|warn|critical` enables controlled owner-notify trigger from evaluator output (default: `none`).
  - `--notify-owner-context "<text>"` passes explicit context to notify helper (Russian text only).
  - `--notify-owner-dry-run` prints readable notify command preview (RU payload) without sending Telegram message.

## Baseline validation flow (Stage 0.4)
- Capture artifact bundle:
  - `.venv\Scripts\python.exe agent\capture_baseline.py --label pre_change`
- Baseline bundle now includes `alert_evaluation.json` from wired evaluator flow and `read_model.json` from Stage 6 publication path.
- Baseline bundle now also includes `schema_snapshot.json` for frontend compatibility checks.
- Baseline bundle now also includes `fixture_bundle.json` with reduced frontend-ready sample payload.
- Bundle output location:
  - `artifacts/baseline/<UTC_TIMESTAMP>_<label>/`
- In serverless runtime, use Object Storage as primary artifact location (local `artifacts/...` is dev-only).
- Fixture bundle helper:
  - `.venv\Scripts\python.exe agent\build_fixture_bundle.py --baseline-root artifacts\baseline`
- Detailed process and checklist:
  - `doc/ops/baseline_validation_and_artifacts.md`
- Routine Stage 5 cadence checklist (per-run/weekly/monthly):
  - `doc/ops/baseline_validation_and_artifacts.md` (`Routine Ops Cadence Checklist`)
- Retry taxonomy metrics checklist (retry/exhausted/transient/permanent/unknown):
  - `doc/05_risk_register.md` (`Retry taxonomy metrics checklist`)
- Weekly retry taxonomy trend thresholds for ops review:
  - `doc/05_risk_register.md` (`Routine cadence enforcement`)

## Secret scan gate (Stage 0.5)
- Pre-commit gate: `detect-secrets` with `.secrets.baseline`.
- Full-repo smoke command:
  - `.venv\Scripts\python.exe -m pre_commit run detect-secrets --all-files`
- Security audit notes:
  - `doc/governance/publication_security_audit.md`

## Deploy workflows
- Test contour workflow: `.github/workflows/deploy_yc_function_main.yml`
  - trigger: `push` to `main`
  - deploy target: `YC_CLOUD_FUNCTION_NAME`
  - contour defaults: `ENV=test`, `API_DOMAIN=API_DOMAIN_TEST`
- Production contour workflow: `.github/workflows/release_yc_function_prod.yml`
  - trigger: `workflow_dispatch` (manual only)
  - deploy target: `YC_CLOUD_FUNCTION_PROD_NAME`
  - contour defaults: `ENV=prod`, `API_DOMAIN=API_DOMAIN_PROD`
- Required GitHub repository variables:
  - `YC_FOLDER_ID`
  - `YC_SERVICE_ACCOUNT_ID` or `YC_RUNTIME_SERVICE_ACCOUNT_ID`
  - `YC_CLOUD_FUNCTION_NAME`
  - `YC_CLOUD_FUNCTION_PROD_NAME`
  - `YC_CLOUD_FUNCTION_PROD_ID`
  - `YC_LOCKBOX_SECRET_ID`
- Runtime app keys (including `SOURCE_SHEET_NAME`, `API_DOMAIN_*`, `YDB_*_TEST`, `YDB_*_PROD`, `STORE_MODE`, `READMODEL_SOURCE`, `NOTIFY_SOURCE`, `RENDER_SOURCE`) are read from Lockbox secret payload.
- Full setup guide:
  - `doc/ops/stage9_main_autodeploy_setup.md`
- Direct cloud endpoint smoke invoke:
  - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
- Migration M3 hash-gate smoke:
  - `.venv\Scripts\python.exe agent\sync_hash_gate_smoke.py`
- Migration M2 parity smoke (legacy-style date parse vs new normalize):
  - `.venv\Scripts\python.exe agent\normalize_parity_smoke.py`
- Stage 22 tri-block parity smoke (API/render/notify from one query contract):
  - `.venv\Scripts\python.exe agent\stage22_tri_block_smoke.py`
- Stage 23 cloud tri-block smoke evidence (function invoke + API v1/v2 parity):
  - `.venv\Scripts\python.exe agent\stage23_cloud_tri_block_smoke.py --function-url <function_url> --api-base <api_base_url>`
- Lockbox sync helper for full `.env` payload:
  - `.venv\Scripts\python.exe agent\sync_lockbox_from_env.py --secret-name DTM`
- Prod release prep helper (validates required prod keys + syncs Lockbox):
  - `.venv\Scripts\python.exe agent\prepare_prod_release.py`
- API Gateway + custom domain helper (test/prod):
  - `.venv\Scripts\python.exe agent\deploy_api_gateway_domain.py --mode test`
  - `.venv\Scripts\python.exe agent\deploy_api_gateway_domain.py --mode prod`
- Frontend HTTP API contract:
  - `doc/ops/frontend_api_contract.md`
  - `docs/api/frontend-v2.md`
  - `docs/api/changelog.md`
- Cloud-side follow-up: publish function version with Lockbox `--secret` mappings and grant runtime service account role `lockbox.payloadViewer` for secret `DTM`.

## Environment contour
- Runtime env selector: `ENV` with allowed values `dev`, `test`, `prod`.
- Base variables are loaded from `.env`.
- Optional profile override is auto-loaded from `.env.<ENV>` when file exists.
- Sheet target selector:
  - `TARGET_SHEET_NAME` is primary target.
  - for `ENV=prod`, when `TARGET_SHEET_NAME` is empty, runtime falls back to `TARGET_SHEET_NAME_PROD`.
- Domain selector:
  - `WEB_DOMAIN` (site domain)
  - `API_DOMAIN_TEST`, `API_DOMAIN_PROD`
  - runtime uses `API_DOMAIN_TEST` for non-prod and `API_DOMAIN_PROD` for prod.
- YDB selector:
  - for `ENV=dev/test` runtime prefers `YDB_ID_TEST`, `YDB_ENDPOINT_TEST`, `YDB_DATABASE_TEST`
  - for `ENV=prod` runtime prefers `YDB_ID_PROD`, `YDB_ENDPOINT_PROD`, `YDB_DATABASE_PROD`
  - legacy fallback `YDB_ID`, `YDB_ENDPOINT`, `YDB_DATABASE` is still supported.
- YDB migration/runtime knobs:
  - `YDB_MIGRATE_ON_START=0|1` (default `0`)
  - `LEGACY_BLOB_WRITE=0|1` (default `0`)
- Timing year inference mode:
  - `TIMING_YEAR_MODE=legacy|anchors|chain` (default: `legacy`)
  - `legacy`: old parser behavior, `next_task_date` pivot by mean.
  - `anchors`: explicit `dd.mm.yyyy` / `dd.mm.yy` anchors + median pivot.
  - `chain`: `anchors` plus guarded year-shift on Jan-Mar future-jump patterns in top-down chain.
- Google service-account key runtime source priority:
  - `GOOGLE_KEY_JSON_PATH` (existing file path)
  - `GOOGLE_KEY_JSON_B64` (base64 JSON text)
  - `GOOGLE_KEY_JSON` (raw JSON text)
  - fallback local file in `key/...json` (dev/local only)
- LLM provider contour:
  - `LLM_PROVIDER=openai|google|yandex` (default: `openai`)
  - OpenAI: `OPENAI_TOKEN`, optional `OPENAI_MODEL` (fallback `gpt-5`)
  - Google: `GOOGLE_LLM_API_KEY`, optional `GOOGLE_LLM_MODEL` (default `gemini-2.0-flash`)
  - Yandex: `YANDEX_LLM_API_KEY`, `YANDEX_LLM_MODEL_URI`
    - if `YANDEX_LLM_MODEL_URI` is empty and `YC_FOLDER_ID` is set, fallback is `gpt://<YC_FOLDER_ID>/yandexgpt/latest`
  - Reliability knobs (all providers):
    - `LLM_HTTP_TIMEOUT_SECONDS` (default `25`)
    - `LLM_HTTP_RETRY_ATTEMPTS` (default `2`)
    - `LLM_HTTP_RETRY_BACKOFF_SECONDS` (default `0.8`)
  - Failover policy knobs:
    - `LLM_FAILOVER_MODE=draft_only|provider` (default `draft_only`)
    - `LLM_FAILOVER_PROVIDER=openai|google|yandex` (used when mode=`provider` and different from primary provider)
- Group chat query contour:
  - `TG_BOT_USERNAME` (without `@`) to enable mention parsing in group messages.

## Group Chat Query (new)
- Works in `group` / `supergroup` chats where bot receives updates.
- Supported commands:
  - `/tasks` or `/tasks@<bot_username>` (`/задачи` alias)
  - `/deadlines` or `/deadlines@<bot_username>` (`/дедлайны` alias)
- Mention mode (requires `TG_BOT_USERNAME`):
  - `@<bot_username> покажи задачи`
  - `@<bot_username> покажи дедлайны`
- Bot replies in the same group chat.
- HTTP API for frontend:
  - `GET /api/v1/frontend` (main payload)
  - `GET /api/v1/read-model` (alias)
  - `GET /api/v1/frontend/doc` (machine-readable contract)
  - `GET /api/v2/frontend` (normalized v2 payload)
  - `GET /api/v2/frontend/doc` (v2 contract page)
- Optional safety guard: set `STRICT_ENV_GUARD=1` to enforce that for `ENV=dev/test` `SOURCE_SHEET_NAME` and `TARGET_SHEET_NAME` are different.
- Templates:
  - `.env.example` (base)
  - `.env.dev.example` (safe local/dev contour)
  - `.env.prod.example` (production contour)

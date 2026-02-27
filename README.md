# Designers Task Manager (DTM)

DTM is a real-world pet project built as a portfolio case about evolving legacy automation into a maintainable product architecture.

## What the project does
- Reads task data from Google Sheets.
- Builds visual planning views for a design team (timeline and designer-focused boards).
- Sends morning reminders to designers via Telegram.
- Uses OpenAI to improve reminder text style, with automatic fallback to draft text when enhancer is unavailable.
- Reminder delivery has in-run duplicate guard (idempotent send key) to prevent repeated sends in one runtime cycle.
- Reminder text enhancement is processed in parallel with bounded concurrency for faster multi-designer runs.
- Reminder delivery now applies bounded retry/backoff for transient Telegram send failures.

## Why this repository exists
- Show practical refactoring of a working legacy system.
- Demonstrate safe migration approach: preserve business behavior while improving code quality.
- Build a foundation for moving from Google Sheets visualization to a dedicated frontend.

## Tech stack
- Python
- Google Sheets / Drive API
- Telegram Bot API
- OpenAI API
- Yandex Cloud / Object Storage

## Engineering focus
- Separation of source and target sheets for safer testing.
- Local test contour for repeatable verification.
- Documentation-first reconstruction plan.
- Security hygiene for public repository readiness.

## Project status
- Production workflow is active.
- Architecture is under phased reconstruction.
- Legacy snapshot is kept in `old/` for controlled comparison during migration.

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
  - `--notify-owner-dry-run` prints notify command without sending Telegram message.

## Baseline validation flow (Stage 0.4)
- Capture artifact bundle:
  - `.venv\Scripts\python.exe agent\capture_baseline.py --label pre_change`
- Baseline bundle now includes `alert_evaluation.json` from wired evaluator flow.
- Bundle output location:
  - `artifacts/baseline/<UTC_TIMESTAMP>_<label>/`
- Detailed process and checklist:
  - `doc/02_baseline_validation_and_artifacts.md`
- Routine Stage 5 cadence checklist (per-run/weekly/monthly):
  - `doc/02_baseline_validation_and_artifacts.md` (`Routine Ops Cadence Checklist`)
- Retry taxonomy metrics checklist (retry/exhausted/transient/permanent/unknown):
  - `doc/05_risk_register.md` (`Retry taxonomy metrics checklist`)

## Secret scan gate (Stage 0.5)
- Pre-commit gate: `detect-secrets` with `.secrets.baseline`.
- Full-repo smoke command:
  - `.venv\Scripts\python.exe -m pre_commit run detect-secrets --all-files`
- Security audit notes:
  - `doc/07_publication_security_audit.md`

## Environment contour
- Runtime env selector: `ENV` with allowed values `dev`, `test`, `prod`.
- Base variables are loaded from `.env`.
- Optional profile override is auto-loaded from `.env.<ENV>` when file exists.
- Optional safety guard: set `STRICT_ENV_GUARD=1` to enforce that for `ENV=dev/test` `SOURCE_SHEET_NAME` and `TARGET_SHEET_NAME` are different.
- Templates:
  - `.env.example` (base)
  - `.env.dev.example` (safe local/dev contour)
  - `.env.prod.example` (production contour)

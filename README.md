# Designers Task Manager (DTM)

DTM is a real-world pet project built as a portfolio case about evolving legacy automation into a maintainable product architecture.

## What the project does
- Reads task data from Google Sheets.
- Builds visual planning views for a design team (timeline and designer-focused boards).
- Sends morning reminders to designers via Telegram.
- Uses OpenAI to improve reminder text style.

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

## Environment contour
- Runtime env selector: `ENV` with allowed values `dev`, `test`, `prod`.
- Base variables are loaded from `.env`.
- Optional profile override is auto-loaded from `.env.<ENV>` when file exists.
- Optional safety guard: set `STRICT_ENV_GUARD=1` to enforce that for `ENV=dev/test` `SOURCE_SHEET_NAME` and `TARGET_SHEET_NAME` are different.
- Templates:
  - `.env.example` (base)
  - `.env.dev.example` (safe local/dev contour)
  - `.env.prod.example` (production contour)

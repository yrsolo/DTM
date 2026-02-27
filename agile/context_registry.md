# Context Registry

Purpose: track freshness and trust of planning sources before TeamLead creates/assigns execution tasks.

## Trust Scale
- `high`: verified against runnable flow/code recently, can be used for execution tasking.
- `medium`: partially verified, safe for planning with explicit assumptions.
- `low`: not verified or conflicting; execution tasking is blocked until verification task is done.

## Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| agile/strategy.md | 2026-02-27 | TeamLead | checked against runnable entrypoints `run_timer.cmd` -> `local_run.py --mode timer` and Stage 0 themes in code/config (`SOURCE_SHEET_NAME`/`TARGET_SHEET_NAME`) | medium | strategy is direction-level and consistent with code shape |
| agile/sprint_current.md | 2026-02-27 | TeamLead | verified board sections and WIP=1 discipline; synchronized DTM-6 lifecycle (`В работе` -> `Готово`) | high | local sprint board is current for this sprint cycle |
| agile/retro.md | 2026-02-27 | TeamLead | retro improvements match implemented process controls (owner escalation, single board discipline) | medium | historical context only; not used as execution truth |
| doc/03_reconstruction_backlog.md | 2026-02-27 | TeamLead | Stage 0 item 0.4 implemented baseline flow status with runnable helper `agent/capture_baseline.py` and smoke evidence | high | roadmap items 0.3 and 0.4 are now covered in sprint outputs |
| README.md | 2026-02-27 | TeamLead | validated local run + baseline flow docs against runnable commands (`local_run.py --mode sync-only --dry-run`, `agent/capture_baseline.py`) | high | operational commands in README align with current runtime |
| Jira control plane | 2026-02-27 | TeamLead | `.env` contains required `JIRA_*` keys; REST check `/rest/api/3/myself` returned `200`; DTM-6 lifecycle/comment updates succeeded via API | high | control plane is available when runtime loads `.env` values |

## Usage Rules
1. Update this file before sprint grooming and before assigning new execution tasks.
2. If required source has `low` trust, create verification task first.
3. Keep evidence short and concrete (command/run/test/doc diff), without secrets.
4. Evidence used in this iteration:
   - `Get-Content local_run.py` and `Get-Content main.py` confirm active run modes include `sync-only` and `reminders-only`, with `dry_run` threading.
   - `git log --oneline -n 8` and `git blame agile/sprint_current.md` used to check recency/drift.
   - `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run` passed; no Google Sheets write requests executed.
   - `.venv\Scripts\python.exe agent\capture_baseline.py --label tsk007_smoke` produced artifact bundle with exit code 0.
   - shell-level `Env:JIRA_*` check may be empty if `.env` is not exported globally; Jira checks should load `.env` explicitly for API validation.

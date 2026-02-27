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
| agile/sprint_current.md | 2026-02-27 | TeamLead | verified board sections and WIP=1 discipline; synchronized DTM-11 lifecycle (`V rabote` -> `Gotovo`) | high | local sprint board is current for this sprint cycle |
| agile/retro.md | 2026-02-27 | TeamLead | retro improvements match implemented process controls (owner escalation, single board discipline) | medium | historical context only; not used as execution truth |
| doc/03_reconstruction_backlog.md | 2026-02-27 | TeamLead | Stage 0 items 0.3, 0.4, 0.5 remain aligned; Stage 1 status extended with DTM-11 reminder runtime compatibility increment | high | backlog status now reflects DTM-8/9/10/11 Stage 1 progress |
| doc/02_current_modules_and_functionality.md | 2026-02-27 | TeamLead | synchronized with repository changes for task/people contracts and reminder runtime fix (`core/repository.py`, `core/people.py`, `core/reminder.py`) | high | module doc covers latest Stage 1 hardening details |
| doc/07_publication_security_audit.md | 2026-02-27 | TeamLead | synchronized with actual pre-commit detect-secrets gate and full-repo smoke command, then validated by smoke run | high | security gate documentation now matches runtime process |
| README.md | 2026-02-27 | TeamLead | validated local run + baseline + security gate docs against runnable commands | high | operational commands in README align with current runtime |
| Jira control plane | 2026-02-27 | TeamLead | `.env` contains required `JIRA_*` keys; REST check `/rest/api/3/myself` returned `200`; DTM-11 lifecycle/comment updates succeeded via API | high | control plane is available when runtime loads `.env` values |

## Usage Rules
1. Update this file before sprint grooming and before assigning new execution tasks.
2. If required source has `low` trust, create verification task first.
3. Keep evidence short and concrete (command/run/test/doc diff), without secrets.
4. Evidence used in this iteration:
   - `Get-Content local_run.py` and `Get-Content main.py` confirm active run modes include `sync-only` and `reminders-only`, with `dry_run` threading.
   - `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run` passed; no Google Sheets write requests executed.
   - `.venv\Scripts\python.exe agent\capture_baseline.py --label tsk007_smoke` produced artifact bundle with exit code 0.
   - `.venv\Scripts\python.exe -m pre_commit run detect-secrets --all-files` passed (`Detect secrets...Passed`).
   - `.venv\Scripts\python.exe -m py_compile core\repository.py` passed after required-column validation changes.
   - `git log --oneline -n 5 -- core/repository.py` + `git blame -L 25,140 core/repository.py` confirm parser/task constructor are active drift points for Stage 1.
   - `.venv\Scripts\python.exe local_run.py --help`, `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run`, and `.venv\Scripts\python.exe local_run.py --mode timer --dry-run` passed after DTM-9 parser/normalization changes.
   - `git log --oneline -n 6 -- core/people.py core/reminder.py` + `git blame -L 1,220 core/people.py` confirm `core/people.py` stayed legacy and needed Stage 1 guardrails.
   - `.venv\Scripts\python.exe -m py_compile core\people.py` and targeted people smoke script passed (`people_smoke_ok`).
   - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run` now passes after reminder runtime compatibility fix (`httpx` proxy setup + unicode-safe logging).
   - shell-level `Env:JIRA_*` check may be empty if `.env` is not exported globally; Jira checks should load `.env` explicitly for API validation.

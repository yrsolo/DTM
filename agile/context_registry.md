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
| agile/sprint_current.md | 2026-02-27 | TeamLead | verified board sections and WIP=1 discipline; updated to reflect Jira access blocker and owner escalation | high | local sprint board now consistent with runtime constraints |
| agile/retro.md | 2026-02-27 | TeamLead | retro improvements match implemented process controls (owner escalation, single board discipline) | medium | historical context only; not used as execution truth |
| doc/03_reconstruction_backlog.md | 2026-02-27 | TeamLead | sampled Stage 0 item 0.3 against code: current CLI supports only `timer/morning/test`, no `sync-only/reminders-only/dry-run` yet | medium | roadmap is useful, each item still requires per-task verification |
| README.md | 2026-02-27 | TeamLead | previously validated against `main.py`, `core/planner.py`, `core/reminder.py`, `config/constants.py`, `utils/storage.py`, `requirements.txt` | high | key behavior and stack claims confirmed against runnable/code artifacts |
| Jira control plane | 2026-02-27 | TeamLead | shell check: `JIRA_BASE_URL/JIRA_EMAIL/JIRA_API_TOKEN/JIRA_PROJECT_KEY` are missing; owner notified via `python agent/notify_owner.py --title "Jira nedostupna (alert)" ...` | low | execution blocked until Jira restored or explicit waiver `LOCAL_ONLY_MODE until <date>` |

## Usage Rules
1. Update this file before sprint grooming and before assigning new execution tasks.
2. If required source has `low` trust, create verification task first.
3. Keep evidence short and concrete (command/run/test/doc diff), without secrets.
4. Evidence used in this iteration:
   - `Get-Content local_run.py` and `Get-Content main.py` confirm active run modes (`timer`, `morning`, `test`) and no dry-run switch.
   - `git log --oneline -n 8` and `git blame agile/sprint_current.md` used to check recency/drift.
   - env check for Jira variables returned all required keys as missing.

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
| agile/sprint_current.md | 2026-02-27 | TeamLead | synchronized with Jira keys/statuses (DTM-2 in progress, DTM-3 todo) and current WIP limit | high | operational board is current for this sprint cycle |
| agile/retro.md | 2026-02-27 | TeamLead | retro improvements match implemented process controls (owner escalation, single board discipline) | medium | historical context only; not used as execution truth |
| doc/03_reconstruction_backlog.md | 2026-02-27 | TeamLead | sampled Stage 0 claims against code: split source/target sheet config exists in `config/constants.py` | medium | use as roadmap; verify each item before execution |
| README.md | 2026-02-27 | TeamLead | validated against `main.py`, `core/planner.py`, `core/reminder.py`, `config/constants.py`, `utils/storage.py`, `requirements.txt`; local run entrypoint clarified (`run_timer.cmd`, `.venv\\Scripts\\python.exe local_run.py --mode timer`) | high | key behavior and stack claims confirmed against runnable/code artifacts |

## Usage Rules
1. Update this file before sprint grooming and before assigning new execution tasks.
2. If required source has `low` trust, create verification task first.
3. Keep evidence short and concrete (command/run/test/doc diff), without secrets.
4. Evidence used in this iteration:
   - `.venv\\Scripts\\python.exe local_run.py --help` (passes)
   - `python local_run.py --help` (fails outside venv due to missing dependency in global env)
   - `config/constants.py` confirms `SOURCE_SHEET_NAME` and `TARGET_SHEET_NAME` split.

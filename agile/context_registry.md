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
| agile/sprint_current.md | 2026-02-27 | TeamLead | verified board sections and WIP=1 discipline; synchronized DTM-15 lifecycle (`V rabote` -> `Gotovo`) | high | local sprint board is current for this sprint cycle |
| agile/retro.md | 2026-02-27 | TeamLead | retro improvements match implemented process controls (owner escalation, single board discipline) | medium | historical context only; not used as execution truth |
| doc/03_reconstruction_backlog.md | 2026-02-27 | TeamLead | Stage 0 items 0.3, 0.4, 0.5 remain aligned; Stage 1 status extended with DTM-13 schema guardrails | high | backlog status now reflects DTM-8/9/10/11/12/13 Stage 1 progress |
| doc/02_current_modules_and_functionality.md | 2026-02-27 | TeamLead | synchronized with repository changes for typed contracts and schema guardrails (`core/contracts.py`, `core/repository.py`, `core/people.py`) | high | module doc covers latest Stage 1 hardening details |
| core/repository.py + core/people.py data-quality diagnostics paths | 2026-02-27 | TeamLead | verified active drift points with `git log --oneline -n 8 -- core/repository.py core/people.py core/contracts.py`, `git blame -L 277,316 core/repository.py`, `git blame -L 56,94 core/people.py`; runnable entrypoint confirmed via `local_run.py --help` | high | safe to execute DTM-14 taxonomy/diagnostics increment |
| core/repository.py + core/people.py row-level mapping paths | 2026-02-27 | TeamLead | re-verified row-construction hotspots with `git blame -L 307,327 core/repository.py` and `git blame -L 57,97 core/people.py`; runtime entrypoint still stable via `local_run.py --help` | high | safe to execute DTM-16 malformed-row fail-soft policy |
| core/repository.py TimingParser + task row accounting paths | 2026-02-27 | TeamLead | validated parser drift points via `git log --oneline -n 8 -- core/repository.py core/errors.py` and active mapping section (`git blame -L 300,360 core/repository.py`); entrypoint check `local_run.py --help` | high | safe to execute DTM-17 timing diagnostics/accounting increment |
| local_run.py + main.py + agent/capture_baseline.py artifact path | 2026-02-27 | TeamLead | checked local entrypoint and artifact flow (`Get-Content local_run.py`, `Get-Content main.py`, `Get-Content agent/capture_baseline.py`, `rg` for diagnostics usage) | high | safe to execute DTM-18 quality report surfacing |
| core/reminder.py + core/planner.py test-mode external integration path | 2026-02-27 | TeamLead | implemented and smoke-verified `mock_external` path (`local_run.py --mode test --dry-run --mock-external`, `--mode reminders-only --dry-run --mock-external`) with skipped Telegram send logs | high | DTM-15 completed; reminder tests can run without external OpenAI/Telegram calls |
| Stage 2 decomposition sources (`doc/03`, `core/planner.py`, `main.py`, `core/repository.py`, `utils/service.py`) | 2026-02-27 | TeamLead | verified drift and coupling via `git log --oneline -n 12 -- core/planner.py core/manager.py core/repository.py core/reminder.py utils/service.py main.py local_run.py`, `git blame` on planner/main/repository hotspots, and import dependency scan (`rg`) | high | safe to execute DTM-19 layer boundary inventory and Stage 2 task decomposition |
| Stage 2 scaffold sources (`doc/10`, `core/planner.py`, `main.py`, `core/manager.py`, `utils/service.py`) | 2026-02-27 | TeamLead | implemented bootstrap boundary (`core/bootstrap.py`) and smoke-verified entrypoint wiring (`local_run.py --mode sync-only --dry-run`, `--mode reminders-only --dry-run --mock-external`) | high | DTM-20 scaffold completed; planner dependency construction is isolated behind bootstrap layer |
| Stage 2 application use-case extraction sources (`main.py`, `core/planner.py`, `core/bootstrap.py`, `local_run.py`) | 2026-02-27 | TeamLead | extracted orchestration to `core/use_cases.py` and smoke-verified mode branches (`local_run.py --mode sync-only --dry-run`, `--mode reminders-only --dry-run --mock-external`) | high | DTM-21 completed; interfaces entrypoint now delegates orchestration to application use-cases |
| Stage 2 infra adapter boundary sources (`core/reminder.py`, `core/bootstrap.py`, `core/use_cases.py`, `main.py`) | 2026-02-27 | TeamLead | implemented adapter contracts (`core/adapters.py`) and smoke-verified injected Telegram/OpenAI wiring (`local_run.py --mode sync-only --dry-run`, `--mode reminders-only --dry-run --mock-external`) | high | DTM-22 completed; external service calls now flow through explicit adapter boundary contracts |
| doc/07_publication_security_audit.md | 2026-02-27 | TeamLead | synchronized with actual pre-commit detect-secrets gate and full-repo smoke command, then validated by smoke run | high | security gate documentation now matches runtime process |
| README.md | 2026-02-27 | TeamLead | validated local run + baseline + security gate docs against runnable commands | high | operational commands in README align with current runtime |
| Jira control plane | 2026-02-27 | TeamLead | `.env` contains required `JIRA_*` keys; REST check `/rest/api/3/myself` returned `200`; DTM-13 lifecycle/comment updates succeeded via API | high | control plane is available when runtime loads `.env` values |

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
   - `git log --oneline -n 8 -- core/repository.py core/people.py core/reminder.py` confirms Stage 1 drift points and latest stabilization commits (`DTM-9..DTM-11`) before planning DTM-12 typed contract scaffold.
   - `.venv\Scripts\python.exe -m py_compile core\contracts.py core\repository.py core\people.py` passed after DTM-12 typed row-contract integration.
   - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run` and `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run` passed after DTM-12 mapping changes.
   - DTM-13 migrated required-header validation to contract metadata (`TaskRowContract.required_columns`, `PersonRowContract.required_columns`) and added fail-fast people sheet validation.
   - shell-level `Env:JIRA_*` check may be empty if `.env` is not exported globally; Jira checks should load `.env` explicitly for API validation.
   - DTM-14 pre-task freshness check completed on current Stage 1 drift points (`core/repository.py`, `core/people.py`, `core/contracts.py`) via git history + blame before decomposition.
   - DTM-16 pre-task freshness check completed on row-level mapping hotspots in `core/repository.py` and `core/people.py` before execution.
   - DTM-16 row-policy smoke script passed (`row_policy_smoke_ok`) with expected skip diagnostics for malformed and duplicate IDs.
   - DTM-17 pre-task freshness check completed on `TimingParser` + `_df_to_task` paths before diagnostics/accounting changes.
   - DTM-17 timing diagnostics smoke passed (`timing_diagnostics_smoke_ok`) and timer/reminder dry-runs stayed green after parser accounting changes.
   - DTM-18 pre-task freshness check completed on local-run and baseline artifact flow before adding quality report output.
   - DTM-18 smoke passed: local run writes `--quality-report-file` JSON and baseline bundle now includes `quality_report.json`.
   - DTM-15 pre-task freshness check completed for reminder external call path and planner wiring before adding test-mode mock controls.
   - DTM-15 smoke passed for mock external reminder flow (`--mock-external`): no real Telegram sends, OpenAI enhancer bypassed by mock agent.
   - DTM-19 pre-task freshness check completed for Stage 2 decomposition sources (planner/main/repository/service coupling and recent drift).
   - DTM-20 pre-task freshness check completed for planner/main dependency-construction boundary (`S2-SLICE-01`).
   - DTM-20 smoke passed after bootstrap extraction scaffold: sync-only dry-run and reminders-only mock dry-run both green.
   - DTM-21 pre-task freshness check completed for main entrypoint orchestration branches before extracting application use-cases.
   - DTM-21 smoke passed after use-case extraction: sync/reminder branches and quality summary output preserved.
   - DTM-22 pre-task freshness check completed for reminder/bootstrap external adapter coupling before extraction.
   - DTM-22 smoke passed after adapter boundary extraction: sync-only dry-run and reminders-only mock run stayed green.

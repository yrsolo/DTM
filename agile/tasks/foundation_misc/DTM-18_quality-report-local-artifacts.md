# DTM-18: Stage 1 quality report surfacing in local run artifacts

## Context
- Stage 1 diagnostics now exist (`row_issues`, timing parse diagnostics), but local runs do not expose them as structured artifact outputs.
- Baseline capture currently stores only dry-run log + meta/checklist.

## Goal
- Surface structured quality report from local run.
- Include quality report in baseline artifact bundle.

## Non-goals
- No business-rule changes in planner scheduling.
- No reminder content changes.

## Mode
- Execution mode

## Plan
1) Add quality report builder around repository/people diagnostics.
2) Return/report this data from local launcher.
3) Include report JSON into `agent/capture_baseline.py` artifact flow.

## Risks
- Report schema drift may affect downstream tooling.
- Some flows may not load people/tasks and produce partial report data.

## Acceptance Criteria
- Local run can emit structured quality report JSON.
- Baseline capture bundle includes quality report artifact.
- Existing dry-run modes remain green.

## Checklist (DoD)
- [x] Quality report generated from runtime diagnostics.
- [x] Local launcher can write report file.
- [x] Baseline capture stores quality report artifact.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-18 created and moved to `V rabote`.
- 2026-02-27: Added planner quality report builder and main runtime summary output.
- 2026-02-27: Added local launcher support for `--quality-report-file` JSON export.
- 2026-02-27: Updated baseline capture helper to persist `quality_report.json` in artifact bundle.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\planner.py main.py local_run.py agent\capture_baseline.py core\repository.py core\people.py core\errors.py`
  - `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run --quality-report-file artifacts\baseline\_tmp_quality_report.json`
  - `.venv\Scripts\python.exe agent\capture_baseline.py --label tsk021_smoke --mode sync-only`
- 2026-02-27: Jira evidence comment added and issue moved to done category (`Gotovo`).

## Links
- Jira: DTM-18
- Sprint: agile/sprint_current.md

# DTM-40: TSK-043 Stage 5 persist SLI trend snapshots across runs

## Context
- Stage 5 already computes reminder SLI summary in `quality_report`.
- Current flow writes only single-run snapshot (`--quality-report-file`) and does not keep trend history.
- Follow-up observability tasks require persisted historical SLI points across multiple runs.

## Goal
- Add reversible persistence for reminder SLI trend snapshots across runs.
- Keep implementation local-run oriented and compatible with existing quality report output.

## Non-goals
- No external monitoring backend integration.
- No alerting threshold evaluator automation in this task.

## Plan
1. Add trend snapshot persistence option in local launcher artifact flow.
2. Add deterministic smoke script validating append/rolling behavior.
3. Sync sprint/context/backlog/docs and Jira evidence.
4. Run reminders-only mock dry-run + trend smoke.

## Checklist (DoD)
- [x] Trend snapshot persistence implemented and documented.
- [x] Deterministic smoke-check added and passing.
- [x] Sprint/context/backlog synchronized.
- [x] Jira lifecycle completed with evidence.

## Work log
- 2026-02-27: Jira `DTM-40` created and moved to `В работе`, start evidence comment added.
- 2026-02-27: Added `--sli-trend-file` and `--sli-trend-limit` to `local_run.py` with rolling snapshot persistence helper.
- 2026-02-27: Added deterministic smoke `agent/reminder_sli_trend_persistence_smoke.py`.
- 2026-02-27: Smoke-checks passed: `py_compile`, trend smoke, and `local_run.py --mode reminders-only --dry-run --mock-external --sli-trend-file ...`.

## Links
- Jira: DTM-40
- Files: local_run.py, README.md, agile/sprint_current.md, agile/context_registry.md, doc/03_reconstruction_backlog.md

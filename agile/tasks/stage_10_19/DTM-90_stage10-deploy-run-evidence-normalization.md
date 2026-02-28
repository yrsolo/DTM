# DTM-90: Stage 10 deploy run evidence normalization report

## Context
- Deploy evidence is currently scattered across chat snippets and raw workflow UI logs.
- Stage 10 needs one reproducible report format for run metadata and key step outcomes.

## Goal
- Add script that exports normalized deploy run evidence JSON from GitHub Actions API.
- Add smoke check and operational usage note.

## Non-goals
- No deploy behavior changes.
- No custom dashboard integration.

## Plan
1. Implement deploy run evidence report builder.
2. Add smoke script to validate report shape.
3. Document command in ops docs.
4. Close Jira lifecycle with evidence.

## Checklist (DoD)
- [x] Jira key exists (`DTM-90`) and moved to `В работе`.
- [x] Report builder script added.
- [x] Smoke script added and passes.
- [x] Ops docs updated with command.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira issue `DTM-90`, moved to `В работе`.
- 2026-02-27: Added `agent/deploy_run_evidence_report.py` and smoke script.
- 2026-02-27: Updated ops checklist and README; Jira moved to `Готово`; owner completion notification sent.

## Links
- Jira: DTM-90
- Files:
  - `agent/deploy_run_evidence_report.py`
  - `agent/deploy_run_evidence_report_smoke.py`

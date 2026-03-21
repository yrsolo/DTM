# DTM-56: TSK-059 Stage 6 slice: read-model JSON contract definition (entities fields versioning)

## Context
- Stage 6 starts from preparing migration to visualization platform.
- Target architecture already states read-model direction but without a concrete contract file.
- Current runtime produces `quality_report` and board outputs, but no canonical read-model artifact contract.

## Goal
- Define canonical read-model JSON contract for Stage 6.
- Fix contract scope: entities, required fields, metadata, schema versioning policy.

## Non-goals
- No runtime builder implementation yet.
- No API endpoint implementation yet.
- No UI implementation yet.

## Plan
1. Run freshness/trust check for Stage 6 sources (`doc/03`, `doc/04`, `core/planner.py`, `local_run.py`).
2. Add a dedicated contract document with stable JSON shape and compatibility rules.
3. Sync sprint/context/backlog and task documentation with Jira lifecycle.
4. Run lightweight smoke checks for impacted command surfaces.

## Checklist (DoD)
- [x] Read-model JSON contract file added with versioning policy.
- [x] Mapping from current runtime artifacts to read-model sections is documented.
- [x] Sprint/context/backlog/task docs synchronized.
- [x] Jira lifecycle complete (`Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ` -> evidence -> `Ð“Ð¾Ñ‚Ð¾Ð²Ð¾`).

## Work log
- 2026-02-27: Jira `DTM-56` created and moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`; start evidence comment posted.
- 2026-02-27: Freshness/trust check started for Stage 6 contract sources.
- 2026-02-27: Added `doc/stages/11_stage6_read_model_contract.md` with canonical JSON shape, entities, mapping notes, and semantic versioning policy.
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe -m py_compile core\planner.py local_run.py`, `.venv\Scripts\python.exe agent\reminder_alert_evaluator.py --help`, `.venv\Scripts\python.exe local_run.py --help`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 2`, `remaining 6`).

## Links
- Jira: DTM-56
- Sources: doc/03_reconstruction_backlog.md, doc/04_target_architecture.md, core/planner.py, local_run.py, agile/sprint_current.md

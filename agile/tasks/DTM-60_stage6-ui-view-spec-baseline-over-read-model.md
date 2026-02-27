# DTM-60: TSK-063 Stage 6 slice: UI view-spec baseline over read-model (filters timeline history)

## Context
- Stage 6 read-model contract is available and partially wired into local artifacts.
- Migration goal requires concrete UI-facing view-spec to avoid ambiguous frontend scope.

## Goal
- Define baseline UI view-spec mapped to read-model sections for:
  - filters,
  - timeline/gantt,
  - change/history panel.

## Non-goals
- No frontend implementation.
- No API backend implementation.

## Plan
1. Verify freshness of contract and architecture sources.
2. Add dedicated UI view-spec document with mapping to read-model fields.
3. Sync sprint/context/backlog/docs and Jira lifecycle.
4. Run lightweight docs/CLI smoke checks.

## Checklist (DoD)
- [x] UI view-spec document added and linked to Stage 6 contract.
- [x] Read-model to UI mapping is explicit for filters/timeline/history.
- [x] Sprint/context/backlog/task docs synchronized.
- [x] Jira lifecycle complete.

## Work log
- 2026-02-27: Jira `DTM-60` created and moved to `В работе`; start evidence comment posted.
- 2026-02-27: Added `doc/12_stage6_ui_view_spec.md` with baseline view-spec for timeline/designer board/task details/alerts + global filters and history baseline.
- 2026-02-27: Smoke sanity-check passed (`.venv\Scripts\python.exe local_run.py --help`, `.venv\Scripts\python.exe agent\read_model_publication_smoke.py`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 6`, `remaining 2`).

## Links
- Jira: DTM-60
- Sources: doc/11_stage6_read_model_contract.md, doc/04_target_architecture.md, agile/sprint_current.md

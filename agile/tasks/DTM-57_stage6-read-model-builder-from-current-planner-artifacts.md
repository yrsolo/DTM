# DTM-57: TSK-060 Stage 6 slice: read-model builder from current planner artifacts

## Context
- Stage 6 JSON contract is defined in `doc/11_stage6_read_model_contract.md`.
- Runtime already produces `quality_report` and optional `alert_evaluation` artifacts.
- A deterministic builder is needed to convert current artifacts into canonical read-model payload.

## Goal
- Implement read-model builder module from existing artifact structures.
- Add deterministic smoke check validating contract-critical fields.

## Non-goals
- No API endpoint publishing yet.
- No UI rendering logic yet.
- No changes to reminder/sync runtime behavior.

## Plan
1. Verify freshness of Stage 6 contract/runtime sources.
2. Implement builder (`quality_report` + optional `alert_evaluation` -> read-model JSON).
3. Add smoke test for builder output shape and key fields.
4. Sync sprint/context/backlog/docs and Jira lifecycle.

## Checklist (DoD)
- [x] Builder module added and returns contract-aligned payload.
- [x] Smoke check validates deterministic output shape.
- [x] Sprint/context/backlog/task docs synchronized.
- [x] Jira lifecycle complete (`В работе` -> evidence -> `Готово`).

## Work log
- 2026-02-27: Jira `DTM-57` created and moved to `В работе`; start evidence comment posted.
- 2026-02-27: Sprint/task synchronization started for Stage 6 builder slice.
- 2026-02-27: Implemented `core/read_model.py` (`build_read_model`) and deterministic smoke `agent/read_model_builder_smoke.py`.
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe -m py_compile core\read_model.py agent\read_model_builder_smoke.py core\planner.py local_run.py`, `.venv\Scripts\python.exe agent\read_model_builder_smoke.py`, `.venv\Scripts\python.exe agent\notify_owner.py --help`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 3`, `remaining 5`).

## Links
- Jira: DTM-57
- Sources: doc/11_stage6_read_model_contract.md, core/planner.py, local_run.py, agile/sprint_current.md, agile/context_registry.md

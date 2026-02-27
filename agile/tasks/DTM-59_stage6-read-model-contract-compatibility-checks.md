# DTM-59: TSK-062 Stage 6 slice: read-model builder contract tests and compatibility checks

## Context
- Stage 6 read-model contract, builder, and publication path are in place.
- Need stable compatibility guard to prevent schema drift and accidental field removals.

## Goal
- Add contract compatibility checks for required read-model fields and basic type/date invariants.
- Add deterministic smoke script for CI/local usage.

## Non-goals
- No API endpoint behavior changes.
- No UI feature implementation.

## Plan
1. Verify contract and builder sources freshness.
2. Implement contract validation helper.
3. Add deterministic compatibility smoke.
4. Sync sprint/context/backlog/Jira.

## Checklist (DoD)
- [x] Contract validation helper implemented.
- [x] Compatibility smoke passes.
- [x] Sprint/context/backlog/task docs synchronized.
- [x] Jira lifecycle complete.

## Work log
- 2026-02-27: Jira `DTM-59` created and moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`; start evidence comment posted.
- 2026-02-27: Sprint/task synchronization started.
- 2026-02-27: Added contract validator `validate_read_model_contract` in `core/read_model.py`.
- 2026-02-27: Added deterministic compatibility smoke `agent/read_model_contract_compat_smoke.py`.
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe -m py_compile core\read_model.py agent\read_model_contract_compat_smoke.py agent\read_model_builder_smoke.py agent\read_model_publication_smoke.py`, `.venv\Scripts\python.exe agent\read_model_contract_compat_smoke.py`, `.venv\Scripts\python.exe agent\read_model_publication_smoke.py`).
- 2026-02-27: Completion Telegram update sent to owner with Stage 6 tracker state (`done 5`, `remaining 3`).

## Links
- Jira: DTM-59
- Sources: core/read_model.py, doc/stages/11_stage6_read_model_contract.md, local_run.py

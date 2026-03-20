# CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1 Evidence

## Trust Gate

- source: `docs/architecture/module-first-recovery/repo-beauty-audit-2026-03-21.md`
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence: beauty audit marks active naming cleanup as priority `2` and `required`
  - trust_level: `high`
  - notes: this wave executes directly from the beauty backlog

- source: active module surfaces and access-api handlers
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/contexts/access_api/module.py`
    - `src/contexts/attachments/module.py`
    - `src/contexts/reminders/module.py`
    - `src/contexts/rendering/module.py`
    - `src/contexts/snapshot/module.py`
    - `src/contexts/telegram_interaction/module.py`
    - `src/contexts/access_api/internal/frontend_v2_handler.py`
    - `src/contexts/access_api/internal/info_handler.py`
    - `src/contexts/access_api/internal/people_snapshot_handler.py`
  - trust_level: `high`
  - notes: enough active code was sampled to keep this wave bounded and smell-specific

## Completed Tasks
- [x] `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P01-T001`
- [x] `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P02-T001`
- [x] `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P02-T002`
- [x] `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P03-T001`
- [x] `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P03-T002`

## Verification

- Executed checks:
  - `python -m unittest tests.entrypoint.test_handler tests.api.test_frontend_api_routing tests.api.test_info_observability tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `rg -n "used during staged migration|Local builder for the .* context|get_snapshot_capability = _get_snapshot_query_capability" src/contexts tests/api`

## Verdict

- before: active module surfaces still described themselves as local builders from a staged migration, and a few access-api query-owned paths still used broad `get_snapshot_capability` naming
- after: active module docstrings now describe present ownership, and access-api query handlers now use `get_snapshot_query_capability` naming where that is the real contract
- next worst thing: active docs still vary a little in tone between calm canon and engineering-note language

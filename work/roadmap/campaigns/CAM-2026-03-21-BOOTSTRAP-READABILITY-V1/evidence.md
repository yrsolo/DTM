# CAM-2026-03-21-BOOTSTRAP-READABILITY-V1 Evidence

## Trust Gate

- source: `docs/architecture/module-first-recovery/repo-beauty-audit-2026-03-21.md`
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence: bootstrap readability is the next remaining high-signal structural beauty smell after top-path, naming, and docs voice cleanup
  - trust_level: `high`
  - notes: the issue is no longer about code ownership, only about readability and finish quality

- source: bootstrap contour and dependent seams
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/platform/bootstrap.py`
    - `src/platform/app_context.py`
    - `tests/api/test_frontend_api_routing.py`
    - `tests/api/test_command_queue_foundation.py`
    - `src/entrypoints/runtime/planner_runtime_entry.py`
  - trust_level: `high`
  - notes: enough code evidence exists to identify the blocker without starting a risky broad rewrite

## Blocker

- `APP_DEPS`, `APP_TRIGGERS`, `build_runtime_app_context`, and shell getters currently act as stable public seams for active tests and entry helpers
- removing or heavily reshaping them would no longer be a local beauty cleanup; it would become a broader DX and test-contract rewrite
- this needs an explicit owner choice between:
  - preserving these seams as an accepted imperfection
  - or allowing a wider cleanup that updates the dependent test surface

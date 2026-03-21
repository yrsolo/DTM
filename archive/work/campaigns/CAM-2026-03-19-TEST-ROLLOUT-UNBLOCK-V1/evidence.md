# CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1 Evidence

## Trust gate
- source: active deploy workflow, active guard scripts, current runtime entrypoint code
- last_verified_at: 2026-03-19
- verified_by: Codex
- evidence:
  - `.github/workflows/deploy_yc_function_main.yml`
  - `scripts/check_no_legacy_entrypoint_imports.py`
  - `index.py`
  - `docs/architecture/runtime/entrypoints.md`
- trust_level: high
- notes:
  - deploy workflow still executes `check_no_legacy_entrypoint_imports.py`
  - current `index.py` follows the modular-monolith contour and no longer matches the historical allowlist baked into the guard

## Completed Tasks
- [x] `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1-P01-T001`
- [x] `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1-P01-T002`
- [x] `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1-P02-T001`
- [x] `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1-P02-T002`
- [x] `CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1-P02-T003`

## Verification
- Command:
  - `python scripts/check_no_monsters.py`
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `python scripts/check_no_legacy_imports.py`
  - `python -m unittest tests.entrypoints.test_import_safety tests.architecture.test_guardrails_v0 -v`
- Result:
  - all local deploy preflight checks passed after aligning `index.py` and the entrypoint guard allowlist with the active runtime contour

## Rollout evidence
- pushed refs:
  - `origin/dev -> db89bd7`
  - `origin/test -> db89bd7`
- workflow:
  - file: `.github/workflows/deploy_yc_function_main.yml`
  - final_run_id: `23309148335`
  - result: `success`
  - url: `https://github.com/yrsolo/DTM/actions/runs/23309148335`
  - notes:
    - initial rollout run `23309016853` also succeeded on pre-closeout SHA `db30731`

## Closeout
- The outdated deploy guard no longer blocks the approved thin-entrypoint contour.
- Canonical `test` deploy is now running from the current modular-monolith head.

## Notes
- Started to unblock `test` rollout after guard preflight failed on the already-approved runtime contour.

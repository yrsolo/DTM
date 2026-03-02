# DTM-198: Stage 21 deploy contour split (test/prod) and API domain tooling

## Context
- Owner requested separate release contour:
  - regular deploy to test function/domain,
  - manual release to production function/domain.
- New env keys were added for prod target sheet and prod function identifiers.

## Goal
- Keep `main` deploy automatic only for test contour.
- Add manual prod release workflow for separate function.
- Add tooling to sync new release keys into Lockbox.
- Add CLI helper to create/update API Gateway and bind test/prod domains.

## Non-goals
- No automatic production deploy on push.
- No business logic changes in planner/reminder flows.
- No destructive cloud changes in repository scripts.

## Plan
1. Update test/prod deploy workflows.
2. Add release prep helper and required-key validation for Lockbox sync.
3. Add API Gateway/domain deployment helper for `test` and `prod`.
4. Refresh docs and agile tracking.

## Checklist (DoD)
- [x] Test auto-deploy workflow uses test contour defaults and required domain variable.
- [x] Manual prod release workflow exists and validates required variables.
- [x] Lockbox sync supports required key assertions.
- [x] Prod release prep script exists and validates new prod keys.
- [x] API Gateway/domain script exists for test/prod.
- [x] README + ops docs updated.
- [x] Sprint/context tracking updated.

## Work log
- 2026-03-02: Added manual workflow `.github/workflows/release_yc_function_prod.yml`.
- 2026-03-02: Updated `.github/workflows/deploy_yc_function_main.yml` for test contour defaults.
- 2026-03-02: Extended `agent/sync_lockbox_from_env.py` with `--require-key`.
- 2026-03-02: Added `agent/prepare_prod_release.py` for release preflight + lockbox sync.
- 2026-03-02: Added `agent/deploy_api_gateway_domain.py` for test/prod API gateway + domain bind.
- 2026-03-02: Updated `.env*.example`, `README.md`, `doc/ops/stage9_main_autodeploy_setup.md`, `doc/02_current_modules_and_functionality.md`.

## Links
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`
- `agent/prepare_prod_release.py`
- `agent/deploy_api_gateway_domain.py`
- `agent/sync_lockbox_from_env.py`

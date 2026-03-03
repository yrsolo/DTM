# DTM-225: Stage 21 split test/prod YDB contours

## Context
- Runtime and deploy workflows used shared `YDB_*` keys for both test and production.
- Need explicit contour split so test/prod can use different databases without manual edits.

## Goal
- Introduce contour-specific YDB keys:
  - `YDB_ID_TEST`, `YDB_ENDPOINT_TEST`, `YDB_DATABASE_TEST`
  - `YDB_ID_PROD`, `YDB_ENDPOINT_PROD`, `YDB_DATABASE_PROD`
- Update runtime resolution, deploy/release workflows, and release-prep checks.
- Sync keys to Lockbox.

## Non-goals
- No runtime behavior changes outside YDB key selection.
- No immediate schema/data migration between databases.

## Plan
1. Update runtime config selector in `config/constants.py`.
2. Update workflows secret mappings for test/prod contours.
3. Update env templates/docs.
4. Sync Lockbox payload and validate prod release precheck.

## Checklist (DoD)
- [x] Runtime uses contour-specific YDB keys with legacy fallback.
- [x] Test workflow maps `YDB_*_TEST` from Lockbox.
- [x] Prod workflow maps `YDB_*_PROD` from Lockbox.
- [x] Prod release prep helper validates `YDB_*_PROD`.
- [x] `.env.example` and docs updated.
- [x] Lockbox synced with new keys.

## Work log
- 2026-03-03: Added contour-aware YDB env resolver in `config/constants.py`.
- 2026-03-03: Updated workflows:
  - `.github/workflows/deploy_yc_function_main.yml` -> `YDB_*_TEST`
  - `.github/workflows/release_yc_function_prod.yml` -> `YDB_*_PROD`
- 2026-03-03: Updated required prod keys in `agent/prepare_prod_release.py`.
- 2026-03-03: Updated `.env.example`, `README.md`, and `doc/ops/stage9_main_autodeploy_setup.md`.
- 2026-03-03: Synced Lockbox from local `.env` (`lockbox_sync_ok`, keys count = 55).
- 2026-03-03: Dry-run release prep passed with new prod YDB key requirements.

## Links
- `config/constants.py`
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`
- `agent/prepare_prod_release.py`
- `.env.example`
- `README.md`
- `doc/ops/stage9_main_autodeploy_setup.md`

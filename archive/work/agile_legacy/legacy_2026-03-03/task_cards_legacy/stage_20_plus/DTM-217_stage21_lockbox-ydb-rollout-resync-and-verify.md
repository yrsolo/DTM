# DTM-217: Stage 21 Lockbox YDB/rollout resync and verification

## Context
- Owner added YDB connection keys in local `.env` and requested guaranteed transfer to Lockbox.
- Deploy workflows must consume YDB and rollout keys from Lockbox for both test/prod contours.

## Goal
- Re-run `.env -> Lockbox` sync with required-key gate for YDB and rollout switches.
- Verify current Lockbox secret version contains required keys.
- Confirm deploy/release workflows map these keys from Lockbox.

## Non-goals
- No runtime rollout switch change in cloud (`STORE_MODE` remains controlled by secret value).
- No immediate prod release execution in this task.

## Plan
1. Run `agent/prepare_prod_release.py --dry-run` to validate required key set.
2. Run `agent/prepare_prod_release.py` to publish new Lockbox version.
3. Verify current Lockbox secret payload entry keys include YDB + rollout keys.
4. Re-check workflow mappings for test/prod deploy.

## Checklist (DoD)
- [x] Required-key dry-run passed.
- [x] Lockbox sync completed successfully.
- [x] Current Lockbox version contains `YDB_ID`, `YDB_ENDPOINT`, `YDB_DATABASE`.
- [x] Current Lockbox version contains `STORE_MODE`, `READMODEL_SOURCE`, `NOTIFY_SOURCE`, `RENDER_SOURCE`.
- [x] Both workflows map these keys from Lockbox.

## Work log
- 2026-03-02: Executed `python agent/prepare_prod_release.py --dry-run`; required key gate passed.
- 2026-03-02: Executed `python agent/prepare_prod_release.py`; new Lockbox version published (`lockbox_sync_ok`).
- 2026-03-02: Verified secret `DTM` current version key list via `yc lockbox secret get --name DTM --format json`.
- 2026-03-02: Confirmed mapping in `.github/workflows/deploy_yc_function_main.yml` and `.github/workflows/release_yc_function_prod.yml`.

## Links
- `agent/prepare_prod_release.py`
- `agent/sync_lockbox_from_env.py`
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`

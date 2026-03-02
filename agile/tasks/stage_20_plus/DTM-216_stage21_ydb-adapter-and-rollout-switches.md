# DTM-216: Stage 21 YDB adapter and rollout switches

## Context
- Owner approved store target: YDB serverless via gRPC SDK.
- Owner approved rollout policy:
  - `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
  - `READMODEL_SOURCE=legacy|ydb`
  - optional `NOTIFY_SOURCE`, `RENDER_SOURCE`

## Goal
- Implement YDB operational store adapter now.
- Keep JSON store as local/mock fallback only.
- Add rollout switches to runtime config and deployment secret mappings.
- Ensure new YDB env keys and rollout keys are synced to Lockbox.

## Non-goals
- No immediate switch to ydb-only in production in this task.

## Plan
1. Add rollout constants and validation in config.
2. Implement YDB adapter + store factory.
3. Switch runtime dual-write branch from old migration flag to `STORE_MODE`.
4. Update test/prod deploy workflows to map YDB and rollout keys from Lockbox.
5. Sync `.env` -> Lockbox and verify keys.

## Checklist (DoD)
- [x] YDB adapter implemented.
- [x] Rollout switches added and validated.
- [x] Workflows read new keys from Lockbox.
- [x] Lockbox sync executed with required keys check.
- [ ] Cloud deploy smoke after workflow run.

## Work log
- 2026-03-02: Implemented `YdbOperationalStore` and store factory with JSON fallback for local/mock.
- 2026-03-02: Added `STORE_MODE/READMODEL_SOURCE/NOTIFY_SOURCE/RENDER_SOURCE` + YDB constants in config.
- 2026-03-02: Updated deploy workflows to inject YDB and rollout keys from Lockbox.
- 2026-03-02: Synced `.env` to Lockbox secret `DTM` with required keys check for `YDB_*` and rollout switches.
- 2026-03-02: Added/updated tests and docs for rollout policy.

## Links
- `src/adapters/store_ydb.py`
- `config/constants.py`
- `main.py`
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`
- `agent/sync_lockbox_from_env.py`

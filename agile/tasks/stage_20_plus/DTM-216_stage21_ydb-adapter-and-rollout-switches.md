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
- [x] Real `dual_write` wrapper writes JSON+YDB with soft secondary errors.
- [x] Read path supports `READMODEL_SOURCE=ydb` for frontend API.
- [x] `ydb_only` has hard-fail in prod when YDB config is missing.
- [x] Workflows read new keys from Lockbox.
- [x] Lockbox sync executed with required keys check.
- [ ] Cloud deploy smoke after workflow run.
- [x] Runtime source switches wired for render/notify (`RENDER_SOURCE`/`NOTIFY_SOURCE`) and tested locally.

## Work log
- 2026-03-02: Implemented `YdbOperationalStore` and store factory with JSON fallback for local/mock.
- 2026-03-02: Added `STORE_MODE/READMODEL_SOURCE/NOTIFY_SOURCE/RENDER_SOURCE` + YDB constants in config.
- 2026-03-02: Updated deploy workflows to inject YDB and rollout keys from Lockbox.
- 2026-03-02: Synced `.env` to Lockbox secret `DTM` with required keys check for `YDB_*` and rollout switches.
- 2026-03-02: Added/updated tests and docs for rollout policy.
- 2026-03-02: Added `DualWriteOperationalStore` (`JSON primary + YDB secondary`) with secondary soft-fail semantics.
- 2026-03-02: Added `list_tasks()` read API for JSON/YDB adapters and wired frontend API read path via `READMODEL_SOURCE=ydb`.
- 2026-03-02: Enforced strict fallback policy: `ydb_only`/`ydb_primary`/`dual_write` require YDB config in prod, fallback to JSON only in non-prod.
- 2026-03-02: Added `StoreTaskRepository` over operational store and switched runtime source plumbing in `main.py`:
  - render pipeline reads from YDB when `RENDER_SOURCE=ydb`,
  - reminder pipeline reads from YDB when `NOTIFY_SOURCE=ydb`,
  - sync write path still uses source sheet repository.
- 2026-03-02: Added unit tests for store repository and source switching (`tests/adapters/test_store_task_repository.py`, `tests/core/test_main_source_switch.py`).
- 2026-03-02: Added explicit YDB auth path via `YC_SA_JSON_CREDENTIALS` (`ServiceAccountCredentials.from_content`) and endpoint normalization (strip `?database=...` from `YDB_ENDPOINT`) for local/runtime compatibility.
- 2026-03-02: Added empty-calendar safety guard for render path when YDB has no tasks yet (`core/manager.py`) + unit test `tests/core/test_manager_calendar_empty.py`.
- 2026-03-02: Added fail-fast YDB retry settings in adapter and removed unconditional `pause` from `run_timer.cmd` (now optional via `RUN_TIMER_PAUSE=1`) to eliminate "silent hanging" behavior.

## Links
- `src/adapters/store_ydb.py`
- `config/constants.py`
- `main.py`
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`
- `agent/sync_lockbox_from_env.py`

# DTM-227: DB migration v2 finalization

## Context
- Owner requested strict execution of `DB_MIGRATION_V2 FINALIZATION` stages with no extra scope.
- Current code already has normalized YDB repos/readmodel path, but lacks full task version archive model and preflight top-50 gate.

## Goal
- Complete stages 0-7 from owner prompt:
  - stage audit,
  - version table and versioning rules,
  - top-50 preflight + daily full sync,
  - forced refresh without version bumps,
  - legacy hot-path disable by default,
  - resilience/smoke/evidence.

## Non-goals
- No API contract redesign outside required migration behavior.
- No unrelated refactor in reminder/render logic.

## Plan
1. Stage 0 audit and document entrypoints.
2. Implement schema/repo/service updates for versions, hashes, preflight/full gate, forced refresh.
3. Wire runtime/index flags and safe behavior.
4. Add tests and smoke hook.
5. Update docs/evidence and sprint/task tracking.

## Checklist (DoD)
- [x] Stage 0 audit documented.
- [x] `dtm_task_versions` schema and repo methods implemented.
- [x] `preflight_hash_50` + `source_hash_full` + daily full-sync logic implemented.
- [x] forced refresh updates data/readmodel without version increments.
- [x] legacy blob-store hot write path disabled by default.
- [x] backoff+jitter and safe defer remain valid.
- [x] unit/smoke tests pass.
- [x] evidence docs updated.

## Work log
- 2026-03-03: Task started, stage 0 audit in progress.
- 2026-03-03: Stage 0 audit documented in `docs/migration_plan.md` (sync/readmodel/api/legacy entrypoints + gaps).
- 2026-03-03: Stage 1 implemented: schema extended (`dtm_task_versions`, expanded `dtm_sync_state`), version archive rules wired in sync service.
- 2026-03-03: Stage 2 implemented: preflight top-50 hash + full hash + daily full-sync gate + TTL skip knobs.
- 2026-03-03: Stage 3 implemented: `force_refresh` path wired (`index.py` -> `main.py` -> sync service) without version bump for existing tasks.
- 2026-03-03: Stage 6 baseline added: unit tests for version/hash rules and cloud smoke script `agent/cloud_smoke_db_migration_v2.py`.
- 2026-03-03: Cloud smoke executed: sync trigger via function URL (`mode=sync-only&force_refresh=1`) + API verify via `https://dtm-api-test.solofarm.ru/api/v2/frontend` (`status=200`, `contractVersion=2.0.1`).
- 2026-03-03: Owner Telegram info-notification sent (`mode=info`, task closeout update).

## Links
- Prompt source: owner chat message "DB_MIGRATION_V2 FINALIZATION (stages + atomic tasks)".

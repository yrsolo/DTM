# Runbook (Current)

This is a minimal runbook to operate the current system.

## 1) Local setup
1) Create `.env.dev` (or copy from `.env.dev.example`).
2) Ensure Google credentials are available via one of:
   - `GOOGLE_KEY_JSON_PATH`
   - `GOOGLE_KEY_JSON_B64`
   - `GOOGLE_KEY_JSON`
3) For YDB access set (test/prod aware):
   - `YDB_ENDPOINT_TEST`, `YDB_DATABASE_TEST` (and/or PROD)
   - optionally `YDB_ID_TEST/PROD`

## 2) Create tables (one-time)
Option A (recommended): run migration mode with env flag:
- set `YDB_MIGRATE_ON_START=1` and run the migrate job (see `main.py` mode).

Option B: call schema ensure via code path (dev only).

## 3) Timer sync + readmodel build
Run job mode that performs:
- hash gate (preflight + full)
- normalize + upsert operational
- build readmodel snapshot

Operational note for current split runtime:
- `mode=timer` in `store_mode=legacy` keeps legacy sheet render/update path.
- `mode=sync-only` is the canonical recovery path for API v2 snapshot rebuild via YDB/readmodel even when `store_mode=legacy`.

Key safety knobs:
- `READMODEL_TTL_MINUTES` (default 9)
- `PREFLIGHT_TOP_ROWS` (default 50)
- `FULL_SYNC_INTERVAL_HOURS` (default 24)
- `FORCE_REFRESH=1` to force rebuild WITHOUT version bumps

## 4) API (frontend v2)
API should read a single row readmodel snapshot from:
- `dtm_readmodel_frontend_v2` (id: `frontend_v2:default`)

If `READMODEL_SOURCE=ydb`, the handler must not rebuild on the fly.

## 5) Milestones invariants
Milestones must never be empty:
- sync adds `start` if missing
- builder synthesizes `start` if milestones_v missing for the current version

## 6) Troubleshooting
### RESOURCE_EXHAUSTED (YDB serverless)
- backoff parameters are controlled by:
  - `YDB_EXHAUSTED_MAX_ATTEMPTS`
  - `YDB_EXHAUSTED_BASE_BACKOFF_SECONDS`
  - `YDB_EXHAUSTED_MAX_BACKOFF_SECONDS`
  - `YDB_EXHAUSTED_JITTER_RATIO`
- reduce query count: prefer readmodel single-row reads, avoid N+1.

### Missing milestones
If logs show `synthetic_start_used` warnings:
- likely milestones_v was not written/backfilled for some tasks.
- run backfill/migration script or investigate sync errors.

## 7) Branching and test deploy
1) Development goes to `dev` (small commits, push to origin).
2) When test contour validation is needed, merge `dev` into `test`.
3) Push `test` to origin:
   - test deploy workflow starts automatically.
4) Production promotion stays owner-controlled: owner manually creates/reviews PR `test -> main`, then runs manual production release workflow.

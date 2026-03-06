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

## 3) Timer update (Snapshot Engine)
Run job mode that performs:
- Sheets snapshot fetch (`values + colors`)
- normalize -> raw snapshot
- prep build (raw + extra merge)
- S3 write for raw/prep snapshots

Operational mode note:
- canonical API v2 data source is S3 prep snapshot.
- `mode=sync-only` remains the explicit manual rebuild mode.

Key safety knobs:
- `READMODEL_TTL_MINUTES` (default 9)
- `PREFLIGHT_TOP_ROWS` (default 50)
- `FULL_SYNC_INTERVAL_HOURS` (default 24)
- `FORCE_REFRESH=1` to force rebuild WITHOUT version bumps

## 4) API (frontend v2)
API reads prep snapshot from S3 via snapshot engine.

Health markers in response:
- `meta.readmodelSource = "s3_snapshot"`
- `meta.sourceHash`
- `meta.sourceId`

## 5) Milestones invariants
Milestones must never be empty:
- sync adds `start` if missing
- builder synthesizes `start` if timing is empty in source

## 6) Troubleshooting
### Snapshot source unavailable
- check Object Storage credentials and bucket/prefix config:
  - `runtime.snapshot_engine.bucket`
  - `runtime.snapshot_engine.prefix_raw|prefix_prep|prefix_extra`
- startup should fail-fast if snapshot engine is enabled but required fields are empty.

### Missing milestones
If logs show synthetic `start`:
- timing payload in source task is empty or not parsed.
- verify source timing text and normalization logs.

## 7) Branching and test deploy
1) Development goes to `dev` (small commits, push to origin).
2) When test contour validation is needed, merge `dev` into `test`.
3) Push `test` to origin:
   - test deploy workflow starts automatically.
4) Production promotion stays owner-controlled: owner manually creates/reviews PR `test -> main`, then runs manual production release workflow.

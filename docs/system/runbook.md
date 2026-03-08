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

## 4.1) Reminder v2
Reminder runtime source:
- tasks from prep snapshot
- people routing from people snapshot (`snapshots/{env}/people/default.json`)

Reminder selection:
- designers are selected only by milestones on today and next workday.
- default statuses: `work`, `pre_done`.

Delivery safety:
- if `ENV=test`, sends are forced to test chat override.
- vacation `да` skips delivery.
- retry policy: 3 attempts with backoff and classified counters.

## 5) Milestones invariants
Milestones must never be empty:
- sync adds `start` if missing
- builder synthesizes `start` if timing is empty in source

## 6) Troubleshooting
### Snapshot source unavailable
- check Object Storage credentials and bucket/prefix config:
  - `runtime.snapshot_engine.bucket`
  - `runtime.snapshot_engine.prefix_raw|prefix_prep|prefix_extra|prefix_people`
- startup should fail-fast if snapshot engine is enabled but required fields are empty.

### Missing milestones
If logs show synthetic `start`:
- timing payload in source task is empty or not parsed.
- verify source timing text and normalization logs.

### Render safety (incident prevention)
- `render_v2` is allowed to write only to worksheet `task_calendar` (`Задачи`).
- `render_v2` must never target `tasks` (`ТАБЛИЧКА`).
- On unsafe target runtime responds with `error.code=render_target_unsafe` and does not write.
- Before release verify source/target spreadsheet separation for prod contour.

## 7) Branching and test deploy
1) Development goes to `dev` (small commits, push to origin).
2) When test contour validation is needed, merge `dev` into `test`.
3) Push `test` to origin:
   - test deploy workflow starts automatically.
4) Production promotion stays owner-controlled: owner manually creates/reviews PR `test -> main`, then runs manual production release workflow.

## 8) Legacy-cut campaign sequence
Execution order for legacy removal:
1) `CAM-LEGACY-CUT-API-V1`
2) `CAM-NOTIFY-MODULE-V1`
3) `CAM-RENDER-MODULE-V1`
4) `CAM-HTTP-FALLBACK-REMOVAL-V1`
5) `CAM-LEGACY-PLANNER-DELETE-V1`

Guard campaign:
- `CAM-GREP-GATES-V1` must be active before planner deletion stage.

## 9) Anti-relapse gate
Run import guard before merge to `test`:
- `python scripts/check_no_legacy_imports.py` (after it is introduced by CAM-GREP-GATES-V1)

Target violations:
- `import core` / `from core`
- `import pandas`
- `GoogleSheetPlanner`
- `build_planner_dependencies`

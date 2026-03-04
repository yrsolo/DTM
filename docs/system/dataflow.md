# Dataflow, Hashing, Versioning (Current)

This document fixes the **canonical path** from Sheets → normalization → hashing/versioning → YDB → readmodel → consumers.

## 1) Sheets snapshot
A source snapshot is treated as:
- `values`: raw cell values for the source-range (task table)
- `colors`: status markers (row/cell colors used to derive task status)

Hashes are computed on raw snapshot (before normalization).

## 2) Hash gate (single canonical gate in SyncService)

### Preflight hash (top rows)
- Fetch top `PREFLIGHT_TOP_ROWS` rows (default 50) of the source-range (values + colors).
- Compute `preflight_hash_50 = stable_json_hash(preflight_snapshot)`.

### Full hash (entire range, conditional)
- Fetch full source-range (values + colors) **only when preflight says full sync is needed**.
- Compute `source_hash_full = stable_json_hash(full_snapshot)` only in this branch.

### Gate decision (operational sync)
Inputs:
- `dtm_sync_state` row for `source_id` (typically one source)
- `preflight_hash_50`
- `source_hash_full`
- `FORCE_REFRESH`
- `FULL_SYNC_INTERVAL_HOURS` (default 24)

Rules (effective):
1) Compute preflight hash and ask canonical gate in `YdbSyncService` (`decide_preflight` / `run_preflight_only`).
2) If not force_refresh AND preflight unchanged AND last full sync not stale → skip full snapshot fetch and skip full sync.
3) Otherwise fetch full snapshot and compute full hash.
4) If not force_refresh AND full hash unchanged → skip normalization/upsert.
5) Else → normalize + write operational tables + build readmodel.

## 3) Normalization invariants
Normalization produces per-task:
- `task_id` (UUID from sheet)
- stable fields: title/brand/format/customer/owner_id/group_id/raw_timing/etc.
- `milestones[]` list
- `status` derived from colors

Invariant: tasks must never have zero milestones.
- If milestones missing, add synthetic `type="start"` milestone.

## 4) Content hash and revision policy

### Content hash
Content hash must include milestones (timing changes matter), but must exclude pure status markers (colors) from triggering version bump.

### Revision policy
For each task_id:
- New task → revision = 1
- If `FORCE_REFRESH=1` → do not bump revision even if content differs
- Else if content_hash changed → revision += 1

## 5) Versioned milestones (no mixing)
Milestones are stored separately and must be tied to the task revision to prevent mixing:
- `dtm_task_milestones_v` keyed by `(task_id, version, idx)`
- active revision is `dtm_tasks.task_revision`

Write ordering for new version (best-effort consistency):
1) write new version record (`dtm_task_versions`)
2) write milestones for `(task_id, new_version)` in `dtm_task_milestones_v`
3) update `dtm_tasks.task_revision = new_version`
4) archive previous version record (optional marker)

## 6) Never-empty milestones guarantee (V1.2)
Two layers:
- Sync ensures at least one milestone (`start`) exists before writing.
- Readmodel builder synthesizes a `start` milestone if `milestones_v` is missing for `(task_id, current_version)`.

## 7) Readmodel build (frontend v2)
Builder does:
1) bulk load `dtm_tasks` head
2) bulk load milestones_v for `(task_id, task_revision)`
3) assemble payload v2 (meta, entities, tasks[] with milestones[])
4) upsert single row into `dtm_readmodel_frontend_v2`

Consumers:
- API v2 reads the snapshot row.
- Render/notify should prefer readmodel or bulk operational reads (no N+1).

## 8) Pipeline skeleton (current transition state)
- `src/app/context.py` defines shared `AppContext` (`cfg`, `deps`, `clock`, `log`).
- `src/services/usecases/contracts.py` defines baseline contracts:
  - `SyncUseCase`, `BuildReadmodelUseCase`, `RenderUseCase`, `NotifyUseCase`.
- `src/entrypoints/jobs/timer_job.py` provides linear `TimerJob.run(ctx)` orchestration shell.

Current runtime keeps legacy execution path, but `main.py` already calls `TimerJob` shell in `timer` mode to anchor the new integration point.

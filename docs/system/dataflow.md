# Dataflow, Hashing, Versioning (Current)

Canonical path: Sheets -> preflight/full hash gate -> normalize -> YDB operational sync -> readmodel snapshot -> API v2 consumers.

## 1) Snapshot and hash inputs
A source snapshot is treated as:
- `values`: raw cell values for the task range
- `colors`: row/cell colors used for status derivation

Hashes are computed on raw snapshot payloads.

## 2) Single canonical gate
Canonical implementation:
- `src/services/sync_service.py` (`YdbSyncService`)
- `dtm_sync_state` in YDB as state source

Preflight phase:
- fetch top rows (`A1:Z<PREFLIGHT_TOP_ROWS>`, default 50)
- compute `preflight_hash_50`
- call `run_preflight_only(...)`

Full phase (conditional):
- full snapshot is fetched only when preflight requires it or force refresh applies
- compute `source_hash_full`
- build normalized tasks from full snapshot

## 3) Canonical timer runtime
Standard runtime object:
- `src/services/timer_pipeline.py` -> `TimerPipeline(AppContext)`
- call shape: `TimerPipeline(ctx).run(RunRequest(mode, force_refresh, task_source))`

Execution order:
1. preflight snapshot fetch
2. gate decision (`run_preflight_only`)
3. optional full snapshot fetch
4. sync operational rows
5. build readmodel snapshot

Evidence logs:
- `full_snapshot_fetch=skipped reason=preflight_unchanged`
- `full_snapshot_fetch=performed reason=sync_required`

## 4) Normalization invariants
Normalization produces per task:
- stable task identity and business fields (`brand`, `format_`, `customer`)
- owner/group/status
- milestones list

Invariant: tasks must never have zero milestones.

## 5) Revision and milestones policy
- revisions are stable per `task_id`
- forced refresh does not bump revision
- milestones are stored by `(task_id, version, idx)`
- readmodel builder reads milestones for active task revision

## 6) Readmodel build
Builder flow:
1. bulk load operational tasks
2. bulk load versioned milestones
3. assemble API v2 payload snapshot
4. upsert one row in readmodel table

API v2 serves the readmodel snapshot.

## 7) Operational sync write strategy
Sync runtime writes operational data in bulk batches only:
- tasks: `upsert_tasks_batch(...)`
- versions: `upsert_task_versions_bulk(...)`
- archive marks: `archive_task_versions_bulk(...)`
- milestones_v: `upsert_task_milestones_versions_bulk(...)`

Runtime path must not do per-task YDB version writes inside task loop.

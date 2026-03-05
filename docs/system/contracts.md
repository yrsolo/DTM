# Contracts (Current)

This document defines the canonical data shapes used in the pipeline.
They are not necessarily 1:1 with Python dataclasses; they represent what the system treats as "truth".

## 1) NormalizedTask (canonical)
Fields (minimum set observed in current code):
- task_id: str (UUID)
- title: str
- brand: str
- format_: str
- customer: str
- owner_id: str
- group_id: str
- raw_timing: str
- status: str (derived from color mapping; normalized workflow status)
- history: str (raw textual status from source column)
- min_date: YYYY-MM-DD? (derived from milestones planned dates)
- max_date: YYYY-MM-DD? (derived from milestones planned dates)
- milestones: list[Milestone]

Notes:
- Some fields may be empty in sheet; still included in hashing basis after normalization.
- `history` is stored as first-class column `dtm_tasks.history`; `raw_payload` is diagnostic only and not a source of truth for `history`.

## 2) Milestone
- idx: int (ordering within task)
- type: str (e.g., start / draft / approve / etc.)
- planned: YYYY-MM-DD? (string in canonical encoding)
- actual: YYYY-MM-DD? (optional)
- status: str (planned/done/...)
- raw_text: str? (optional)

Invariants:
- milestones array must never be empty (at least a synthetic "start").

## 3) Hash contracts

### stable_json_hash(values)
- Used for source snapshots.
- Must be stable across platforms: JSON dump with sorted keys and fixed separators.

### content_hash(task_fields + milestones_fields)
- Used for versioning.
- Must include milestones fields (timing changes matter).
- Must exclude pure status markers (row color) from causing version bump.

## 4) Query filters (frontend API v2)
Minimal supported filtering behavior (as per current API design):
- time window: window_start/window_end, mode intersects (task included if its start/end intersects)
- status filters may be applied by consumers (active/archived)

## 5) YDB table contracts (what each row represents)

### dtm_tasks row = HEAD state
Represents the latest canonical task state as of last successful sync.

### dtm_task_versions row = Immutable version record
Represents one version snapshot of the task (payload_json + content_hash), optionally marked archive.

### dtm_task_milestones_v row = Immutable milestones for (task_id, version)
Represents one milestone entry for a specific task version.

### dtm_readmodel_frontend_v2 row = View snapshot
Represents a full payload JSON snapshot for frontend/API consumption.

## 6) Runtime modes (contract-level view)
See `docs/system/runtime_modes.md` for the mapping of modes to use-cases and data sources.

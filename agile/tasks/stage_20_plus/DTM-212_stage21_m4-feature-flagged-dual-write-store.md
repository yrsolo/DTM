# DTM-212: Stage 21 M4 feature-flagged dual-write store

## Context
- M4 requires gradual introduction of operational store writes without breaking current flow.
- Runtime needed a safe, optional dual-write path to the minimal JSON store.

## Goal
- Add `MIGRATION_DUAL_WRITE_STORE` runtime branch in `main.py`.
- Serialize current task snapshot into store records and upsert to JSON store file.
- Keep default behavior unchanged (`flag=0`).

## Non-goals
- No mandatory store write in production.
- No read-model switch to store in this task.

## Plan
1. Add store file config env.
2. Add task->store record converter in runtime.
3. Gate dual-write branch by existing migration flag.

## Checklist (DoD)
- [x] Config constants/env example updated.
- [x] Runtime dual-write branch added behind flag.
- [x] Existing tests and smoke checks remain green.

## Work log
- 2026-03-02: Added `MIGRATION_STORE_FILE` config and env template entry.
- 2026-03-02: Added `_task_to_store_record` and dual-write branch in `main.py`.
- 2026-03-02: Verified regression tests and smokes stay green.

## Links
- `main.py`
- `config/constants.py`
- `.env.example`

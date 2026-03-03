# CAM-MILESTONES-V1.2 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `src/services/sync_service.py` + `src/services/readmodel_builder.py` + `src/adapters/ydb/operational_repo.py` | 2026-03-03 | TeamLead agent | code+tests+cloud smoke for R1/R2/R3 hardening | high | defaults now favor lower YDB quota usage and safer milestone consistency |

## Execution Log
- Added config flag `WRITE_LEGACY_MILESTONES` (default `0`) and wired it into sync runtime.
- Legacy milestones write is now explicitly skipped by default:
  - `legacy_milestones_write=skipped reason=disabled`.
- Builder now guarantees fallback synthetic milestone `start` when `(task_id, current_version)` has no rows.
- Sync now fails fast on zero-written milestones_v for version bump:
  - `RuntimeError("milestones_write_empty")`.
- Version bump consistency hardened:
  - write new version + milestones_v before archive old version,
  - verify `current_version` and matching milestones_v rows after write.
- Validation:
  - `.venv\Scripts\python.exe -m tests.services.test_sync_source_hash_gate` (8 tests, OK)
  - `.venv\Scripts\python.exe -m tests.services.test_readmodel_uses_milestones_table` (2 tests, OK)
  - `.venv\Scripts\python.exe -m tests.adapters.test_ydb_operational_repo_milestones_bulk` (OK)
  - `.venv\Scripts\python.exe -m tests.api.test_frontend_api_routing` (10 tests, OK)
  - cloud smoke `sync-only(force_refresh=1) -> api/v2`: `200/200`, `api_ok=true`.

## Completion Checklist
- [x] P01 completed
- [x] P02 completed
- [x] P03 completed
- [x] P04 completed

# CAM-DBMIG-MILESTONES-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `docs/db/schema.md` + `src/adapters/ydb/*` + `src/services/readmodel_builder.py` | 2026-03-03 | TeamLead agent | repo scan against current CAM backlog and rollout objectives; no conflicting active doc source found outside `docs/*` | medium | campaign execution starts after first schema/task slice is implemented |

## Execution Log
- campaign scaffold created (`charter.md`, `plan.md`, `evidence.md`)
- queue seeded in `work/roadmap/backlog.md` and `work/now/tasks.md`
- P01 schema/model alignment completed:
  - added `dtm_task_milestones_v` to YDB DDL (`src/adapters/ydb/schema.py`)
  - fixed repo contract alias `current_version` = `task_revision` (`src/adapters/ydb/operational_repo.py`)
  - documented version truth and legacy milestones compatibility role (`docs/db/schema.md`, `docs/db/migration-plan.md`)
- P02 write-path versioning completed:
  - sync writes `milestones_v` only when `create_new_version` is true and refresh is not forced (`src/services/sync_service.py`)
  - status/color-only update path keeps version stable and skips versioned milestones writes
  - forced refresh path skips version table and `milestones_v` writes for existing tasks
  - regression tests updated and passed via `python -m tests.services.test_sync_source_hash_gate`
- P03 readmodel source-of-truth completed:
  - readmodel builder loads milestones strictly from `dtm_task_milestones_v` by `(task_id, current_version)` (`src/services/readmodel_builder.py`)
  - operational repo got bulk versioned milestones loader (`list_milestones_for_versions`) with bounded query profile (`src/adapters/ydb/operational_repo.py`)
  - legacy/raw payload milestone source is removed from builder hot path (no raw fallback used for v2 readmodel build)
  - regression test updated for version-aware milestones source:
    - `.venv\Scripts\python.exe -m tests.services.test_readmodel_uses_milestones_table`
    - `.venv\Scripts\python.exe -m tests.services.test_sync_source_hash_gate`
  - smoke path validated:
    - `.venv\Scripts\python.exe agent/cloud_smoke_db_migration_v2.py --base-url https://functions.yandexcloud.net/<YC_CLOUD_FUNCTION_ID> --api-url https://<API_DOMAIN_TEST>/api/v2/frontend`
    - result: `sync_status_code=200`, `api_status_code=200`, `api_contract_version=2.0.1`, `api_ok=true`
- P04 migration/backfill completed:
  - added migration utility `agent/backfill_milestones_versions.py`
    - reads current versions from `dtm_tasks`
    - migrates legacy rows from `dtm_task_milestones` into `dtm_task_milestones_v` keyed by `(task_id, version)`
    - supports verification sample to detect cross-version timing mismatch
  - fixed YDB date normalization for integer-encoded Date values in operational adapter (`src/adapters/ydb/operational_repo.py`)
  - executed migration flow on YDB contour:
    - `main(mode='db_migrate')` -> `db_migrate_done=true`
    - forced sync in `STORE_MODE=ydb_primary` produced operational rows (`tasks_upserted=999`, `milestones_upserted=5732`)
    - backfill run with verification:
      - `rows_written=5732`
      - `verify_sample_size=5`
      - `verify_matches=5`, `verify_mismatches=0`, `verify_ok=true`
  - added date-conversion regression test:
    - `.venv\Scripts\python.exe -m tests.adapters.test_ydb_operational_repo_dates`
- P05 tests/evidence package completed:
  - builder-level version guard is enforced and tested:
    - mismatched milestone row versions are ignored (`src/services/readmodel_builder.py`)
    - `.venv\Scripts\python.exe -m tests.services.test_readmodel_uses_milestones_table`
  - forced refresh version stability regression remains green:
    - `.venv\Scripts\python.exe -m tests.services.test_sync_source_hash_gate`
  - runbook updated with one-time versioned milestones backfill procedure:
    - `docs/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`

## Completion Checklist
- [x] P01 schema tasks done
- [x] P02 write-path versioning tasks done
- [x] P03 readmodel source-of-truth tasks done
- [x] P04 migration/backfill tasks done
- [x] P05 tests and evidence package done

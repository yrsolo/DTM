# CAM-DBMIG-MILESTONES-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `docs/db/schema.md` + `src/adapters/ydb/*` + `src/services/readmodel_builder.py` | 2026-03-03 | TeamLead agent | repo scan against current CAM backlog and rollout objectives; no conflicting active doc source found outside `docs/*` | medium | campaign execution starts after first schema/task slice is implemented |

## Execution Log
- campaign scaffold created (`charter.md`, `plan.md`, `evidence.md`)
- queue seeded in `agile/backlog.md` and `agile/sprint_current.md`
- P01 schema/model alignment completed:
  - added `dtm_task_milestones_v` to YDB DDL (`src/adapters/ydb/schema.py`)
  - fixed repo contract alias `current_version` = `task_revision` (`src/adapters/ydb/operational_repo.py`)
  - documented version truth and legacy milestones compatibility role (`docs/db/schema.md`, `docs/db/migration-plan.md`)
- P02 write-path versioning completed:
  - sync writes `milestones_v` only when `create_new_version` is true and refresh is not forced (`src/services/sync_service.py`)
  - status/color-only update path keeps version stable and skips versioned milestones writes
  - forced refresh path skips version table and `milestones_v` writes for existing tasks
  - regression tests updated and passed via `python -m tests.services.test_sync_source_hash_gate`

## Completion Checklist
- [x] P01 schema tasks done
- [x] P02 write-path versioning tasks done
- [ ] P03 readmodel source-of-truth tasks done
- [ ] P04 migration/backfill tasks done
- [ ] P05 tests and evidence package done

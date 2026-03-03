# CAM-MILESTONES-V1.1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `src/adapters/ydb/operational_repo.py` + `src/services/readmodel_builder.py` | 2026-03-03 | TeamLead agent | code scan confirms milestones_v read path and sync policy already active from previous campaign | high | V1.1 focuses on cleanup hardening + migration utility |

## Execution Log
- campaign scaffolding created (`charter.md`, `plan.md`, `evidence.md`).
- implemented safe bulk milestone replace: no global delete, only delete by affected `task_id` set.
- added migration utility `agent/migrate_milestones_to_v.py`:
  - source priority: `dtm_task_milestones` first, fallback to `raw_payload["milestones"]`.
  - idempotent upsert semantics via PK `(task_id, version, idx)`.
- executed migration utility on current contour:
  - `tasks_total=999`
  - `rows_prepared=5732`
  - `rows_written=5732`
  - verification sample: `verify_matches=10`, `verify_mismatches=0`.
- smoke path re-validated:
  - `agent/cloud_smoke_db_migration_v2.py`
  - `sync_status_code=200`, `api_status_code=200`, `api_contract_version=2.0.1`, `api_ok=true`.

## Completion Checklist
- [x] P01 data model/schema checks completed
- [x] P02 sync safety updates completed
- [x] P03 readmodel source-of-truth checks completed
- [x] P04 migration and verification completed
- [x] P05 tests/smoke/evidence completed

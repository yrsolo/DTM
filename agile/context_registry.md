# Context Registry (Active)

| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `src/services/readmodel_builder.py` | 2026-03-03 | TeamLead agent | verified builder reads milestones via `list_milestones_for_versions(task_id,current_version)`; local tests + cloud smoke passed | high | source-of-truth moved to `dtm_task_milestones_v` for v2 readmodel build |
| `src/adapters/ydb/operational_repo.py` | 2026-03-03 | TeamLead agent | added and validated bulk query loader for versioned milestones; no per-task N+1 path in builder | high | fallback to legacy milestones table intentionally not used in readmodel builder |
| `docs/campaigns/CAM-DBMIG-MILESTONES-V1/plan.md` | 2026-03-03 | TeamLead agent | cross-check against implementation and sprint queue: P01/P02/P03 completed, P04/P05 pending | medium | keep synchronized after each campaign slice completion |
| `agent/backfill_milestones_versions.py` + `src/adapters/ydb/operational_repo.py` | 2026-03-03 | TeamLead agent | executed db_migrate, forced sync on ydb contour, then backfill: `rows_written=5732`, verification sample `5/5` matches | high | P04 migration path verified on live YDB contour with backoff logs present but successful completion |
| `docs/ops/stage22_db_migrate_force_refresh_rollback_runbook.md` + `tests/services/test_readmodel_uses_milestones_table.py` | 2026-03-03 | TeamLead agent | added explicit backfill runbook step and confirmed builder ignores mismatched milestone versions in test | high | P05 evidence package complete and tied to executable checks |
| `docs/campaigns/CAM-MILESTONES-V1.1/*` + `src/adapters/ydb/operational_repo.py` | 2026-03-03 | TeamLead agent | verified V1 baseline completed; V1.1 opened for hardening gaps (global delete risk + migration fallback utility) | high | execution starts from P02-T004 in current sprint |
| `agent/migrate_milestones_to_v.py` + `docs/evidence/CAM-MILESTONES-V1.1.md` | 2026-03-03 | TeamLead agent | migration executed with `rows_written=5732` and verification sample `10/10`; cloud smoke returned `api_ok=true` | high | campaign closeout evidence published for V1.1 |

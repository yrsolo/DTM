# Context Registry (Active)

| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `src/services/readmodel_builder.py` | 2026-03-03 | TeamLead agent | verified builder reads milestones via `list_milestones_for_versions(task_id,current_version)`; local tests + cloud smoke passed | high | source-of-truth moved to `dtm_task_milestones_v` for v2 readmodel build |
| `src/adapters/ydb/operational_repo.py` | 2026-03-03 | TeamLead agent | added and validated bulk query loader for versioned milestones; no per-task N+1 path in builder | high | fallback to legacy milestones table intentionally not used in readmodel builder |
| `docs/campaigns/CAM-DBMIG-MILESTONES-V1/plan.md` | 2026-03-03 | TeamLead agent | cross-check against implementation and sprint queue: P01/P02/P03 completed, P04/P05 pending | medium | keep synchronized after each campaign slice completion |

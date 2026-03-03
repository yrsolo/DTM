# CAM-DOC-REFORM Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `README.md`, `docs/README.md`, `work/README.md`, `work/now/tasks.md`, `work/roadmap/backlog.md` | 2026-03-03 | TeamLead agent | direct file read + `rg` scan on active tree + `git log -n 12` drift check | high | active control plane converged to CAM-P-T |
| `agent/OPERATING_CONTRACT.md`, `AGENTS.md`, `agent/teamlead.md` | 2026-03-03 | TeamLead agent | runtime contract reread after CAM migration and path updates | high | execution rules align with new docs/agile structure |

## Checklist
- [x] `CAM-DOC-REFORM-P01-T001` CAM-P-T rules and templates added.
- [x] `CAM-DOC-REFORM-P01-T002` campaign folder and charter/plan/evidence created.
- [x] `CAM-DOC-REFORM-P01-T003` active `docs/` map created.
- [x] `CAM-DOC-REFORM-P01-T004` legacy `doc/` archived and stub created.
- [x] `CAM-DOC-REFORM-P02-T001` conflicting migration docs archived and active path normalized.
- [x] `CAM-DOC-REFORM-P02-T002` process control plane moved to `work/`; legacy moved to archive.
- [x] `CAM-DOC-REFORM-P02-T003` root README entrypoints updated.

## Move Evidence
- `git mv doc docs/archive/doc_legacy`
- `git mv docs/evidence_db_migration_v2.md docs/evidence/db_migration_v2.md`
- `git mv docs/migration_plan.md docs/archive/migration_legacy/migration_plan.md`
- `git mv docs/migration/plan.md docs/archive/migration_legacy/plan.md`
- `git mv docs/migration/tasks.md docs/archive/migration_legacy/tasks.md`
- `git mv agile/strategy.md work/archive/agile_legacy/legacy_2026-03-03/strategy.md`
- `git mv agile/retro.md work/archive/agile_legacy/legacy_2026-03-03/retro.md`
- `git mv agile/context_registry.md work/archive/agile_legacy/legacy_2026-03-03/context_registry.md`
- `git mv agile/tasks work/archive/agile_legacy/legacy_2026-03-03/task_cards_legacy`

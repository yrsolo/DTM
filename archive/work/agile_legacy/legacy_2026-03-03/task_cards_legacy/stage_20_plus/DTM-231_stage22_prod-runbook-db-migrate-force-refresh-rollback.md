# DTM-231: Stage 22 production runbook for db_migrate / forced refresh / rollback

## Context
- Stage 22 requires explicit operational procedure for DB migration lifecycle and safety gates.
- Existing docs had migration pieces, but no single concise operator flow for migrate + forced refresh + rollback.

## Goal
- Publish one practical runbook for:
  - `db_migrate`,
  - forced refresh (`force_refresh=1`),
  - rollback to stable source-policy contour.
- Wire references from active docs.

## Non-goals
- No runtime behavior changes.
- No workflow trigger changes.

## Plan
1. Draft concise runbook in `doc/ops`.
2. Add safety gates and expected log markers.
3. Link runbook from `README.md` and DB migration plan doc.

## Checklist (DoD)
- [x] New runbook file created in `doc/ops`.
- [x] Includes migrate/forced-refresh/rollback procedures.
- [x] Includes pre-check safety gates and post-checklist.
- [x] References added in `README.md` and `docs/db/migration-plan.md`.

## Work log
- 2026-03-03: Added `doc/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`.
- 2026-03-03: Added runbook links in `README.md` and `docs/db/migration-plan.md`.

## Links
- Runbook: `doc/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`

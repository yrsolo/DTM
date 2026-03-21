# CAM-P-T Planning System

## ID Rules
- Campaign: `CAM-<NAME>`
- Phase: `P01..P99`
- Task: `T001..T999`
- Full task ID: `CAM-<NAME>-P##-T###`

## Numbering Policy
- IDs are immutable after publication.
- Reserved range per phase:
  - `T800..T899` for planned inserts/hotfix tasks
  - `T900..T999` for unplanned debt/incident follow-up
- Area tags (`area:DB`, `area:API`, `area:DOC`, `area:OPS`) are metadata only and never replace numbering.

## Required Campaign Files
- `charter.md` - scope, goals, non-goals, exit criteria.
- `plan.md` - phased task breakdown with CAM IDs.
- `evidence.md` - execution proof and completion checklist.

## Templates
- `docs/campaigns/_template/charter.md`
- `docs/campaigns/_template/plan.md`
- `docs/campaigns/_template/evidence.md`


# CAM-DBMIG-MILESTONES-V1 Plan

## P01 - Schema and model alignment
- `CAM-DBMIG-MILESTONES-V1-P01-T001` add `dtm_task_milestones_v(task_id, version, idx, type, planned_at, actual_at, status, ...)`.
- `CAM-DBMIG-MILESTONES-V1-P01-T002` codify `dtm_tasks.current_version` as active truth for milestone selection.
- `CAM-DBMIG-MILESTONES-V1-P01-T003` set compatibility role of legacy `dtm_task_milestones` (no readmodel dependency).

## P02 - Sync/write path version atomicity
- `CAM-DBMIG-MILESTONES-V1-P02-T001` on content/timing change create new task version and write milestones for new version.
- `CAM-DBMIG-MILESTONES-V1-P02-T002` on status/color-only update keep version unchanged and do not write new milestone version.
- `CAM-DBMIG-MILESTONES-V1-P02-T003` forced refresh updates snapshots/operational state without version increment and without new `*_v` rows.

## P03 - Readmodel builder source of truth
- `CAM-DBMIG-MILESTONES-V1-P03-T001` builder loads milestones from `dtm_task_milestones_v` by `current_version`.
- `CAM-DBMIG-MILESTONES-V1-P03-T002` remove raw payload milestone fallback as source of truth.
- `CAM-DBMIG-MILESTONES-V1-P03-T003` smoke path: sync -> readmodel build -> `/api/v2/frontend`.

## P04 - Data migration for existing rows
- `CAM-DBMIG-MILESTONES-V1-P04-T001` migration script to backfill versioned milestones from current data.
- `CAM-DBMIG-MILESTONES-V1-P04-T002` verification sample on selected tasks to prove no mixed timing versions.

## P05 - Tests and evidence
- `CAM-DBMIG-MILESTONES-V1-P05-T001` unit test: version update uses matching milestone version in builder.
- `CAM-DBMIG-MILESTONES-V1-P05-T002` unit test: forced refresh keeps versions stable.
- `CAM-DBMIG-MILESTONES-V1-P05-T003` publish evidence document and runbook snippet.


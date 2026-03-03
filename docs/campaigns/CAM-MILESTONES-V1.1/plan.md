# CAM-MILESTONES-V1.1 Plan

## P01 - Data model and schema
- `CAM-MILESTONES-V1.1-P01-T001` confirm `dtm_task_milestones_v` schema in active DDL.
- `CAM-MILESTONES-V1.1-P01-T002` confirm single active version field in `dtm_tasks` (`current_version` alias).
- `CAM-MILESTONES-V1.1-P01-T003` mark `dtm_task_milestones` as compatibility-only in docs.

## P02 - Sync write-path safety
- `CAM-MILESTONES-V1.1-P02-T001` keep versioned milestones writes only for new content/timing versions.
- `CAM-MILESTONES-V1.1-P02-T002` keep status/color-only path without new milestone versions.
- `CAM-MILESTONES-V1.1-P02-T003` keep forced-refresh without version mutation.
- `CAM-MILESTONES-V1.1-P02-T004` remove global milestones DELETE; delete only affected task ids.

## P03 - Readmodel single source of truth
- `CAM-MILESTONES-V1.1-P03-T001` read milestones by `(task_id, current_version)` from `dtm_task_milestones_v`.
- `CAM-MILESTONES-V1.1-P03-T002` ensure builder has no dependency on `raw_payload["milestones"]`.
- `CAM-MILESTONES-V1.1-P03-T003` keep `entities.enums.milestoneType` derived from actually returned milestones.

## P04 - Existing data migration
- `CAM-MILESTONES-V1.1-P04-T001` add migration utility with source priority: `dtm_task_milestones` then `raw_payload["milestones"]`.
- `CAM-MILESTONES-V1.1-P04-T002` verify migrated milestones on sampled tasks and publish evidence.

## P05 - Tests, smoke, evidence
- `CAM-MILESTONES-V1.1-P05-T001` unit tests for version-consistent readmodel milestone selection.
- `CAM-MILESTONES-V1.1-P05-T002` unit tests for forced-refresh non-mutation behavior.
- `CAM-MILESTONES-V1.1-P05-T003` smoke + evidence publication.

# CAM-MILESTONES-V1.2 Plan

## P01 - Disable legacy milestones hot write
- `CAM-MILESTONES-V1.2-P01-T001` add `WRITE_LEGACY_MILESTONES` config flag (default `false`).
- `CAM-MILESTONES-V1.2-P01-T002` gate `replace_task_milestones_bulk` by flag and log skip.
- `CAM-MILESTONES-V1.2-P01-T003` document legacy table as compat-only in active docs.

## P02 - No-empty milestones guarantee
- `CAM-MILESTONES-V1.2-P02-T001` builder synthetic `start` fallback + warning/log counters.
- `CAM-MILESTONES-V1.2-P02-T002` sync assert: version bump must write non-empty milestones_v.

## P03 - Best-effort consistency without transactions
- `CAM-MILESTONES-V1.2-P03-T001` reorder bump flow:
  - create new version row,
  - write milestones_v,
  - update `dtm_tasks.current_version`,
  - archive previous version.
- `CAM-MILESTONES-V1.2-P03-T002` post-write guard:
  - changed tasks must have `current_version`,
  - milestones_v must exist for `(task_id, current_version)`.

## P04 - Tests and evidence
- `CAM-MILESTONES-V1.2-P04-T001` builder unit test for synthetic `start`.
- `CAM-MILESTONES-V1.2-P04-T002` sync unit test for `milestones_write_empty`.
- `CAM-MILESTONES-V1.2-P04-T003` sync unit test for `WRITE_LEGACY_MILESTONES=false`.
- `CAM-MILESTONES-V1.2-P04-T004` publish `docs/evidence/CAM-MILESTONES-V1.2.md`.

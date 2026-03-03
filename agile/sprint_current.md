# Sprint Current

## Sprint Goal
Complete CAM transition of planning/docs and start execution-ready queue for milestone versioning campaign.

## Capacity
1 active execution task (WIP=1).

## Now
- [DONE] `CAM-DOC-REFORM-P01-T001` CAM-P-T rules + templates.
- [DONE] `CAM-DOC-REFORM-P01-T002` campaign shell for doc reform.
- [DONE] `CAM-DOC-REFORM-P01-T003` active docs structure + single docs map.
- [DONE] `CAM-DOC-REFORM-P01-T004` archive legacy `doc/` and create deprecation stub.
- [DONE] `CAM-DOC-REFORM-P02-T001` normalize migration docs and archive conflicts.
- [DONE] `CAM-DOC-REFORM-P02-T002` clean `agile/` active surface and archive legacy files.
- [DONE] `CAM-DOC-REFORM-P02-T003` refresh README entrypoints.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T001` add versioned milestones table `dtm_task_milestones_v` in schema.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T002` codify `current_version` truth rule (`task_revision` alias).
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T003` define legacy milestones compatibility role.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T001` content/timing change writes milestone versions.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T002` status/color-only updates do not create milestone versions.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T003` forced refresh keeps versions and skips milestones_v writes.

## Done (Latest)
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T001`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T001`
- [DONE] `CAM-DOC-REFORM-P02-T003`
- [DONE] `CAM-DOC-REFORM-P02-T002`
- [DONE] `CAM-DOC-REFORM-P02-T001`
- [DONE] `CAM-DOC-REFORM-P01-T004`
- [DONE] `CAM-DOC-REFORM-P01-T003`
- [DONE] `CAM-DOC-REFORM-P01-T002`
- [DONE] `CAM-DOC-REFORM-P01-T001`

## Blocked
- none

## Next 3-5 Tasks (Groomed)
- [TODO] `CAM-DBMIG-MILESTONES-V1-P03-T001` readmodel builder join by current version.
- [TODO] `CAM-DBMIG-MILESTONES-V1-P03-T002` remove raw payload fallback as milestone source of truth.
- [TODO] `CAM-DBMIG-MILESTONES-V1-P03-T003` smoke path sync -> build -> api/v2.
- [TODO] `CAM-DBMIG-MILESTONES-V1-P04-T001` backfill script for milestones_v.

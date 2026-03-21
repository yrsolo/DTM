# Sprint Current

## Sprint Goal
Execute CAM-MILESTONES-V1.2 hardening for milestones_v safety and quota-friendly sync path.

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
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T001` readmodel builder join by current version.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T002` remove raw payload fallback as milestone source of truth.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T003` smoke path sync -> build -> api/v2.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P04-T001` backfill script for milestones_v.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P04-T002` verification sample proving no mixed timing versions.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T001` unit test: version update uses matching milestone version in builder.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T002` unit test: forced refresh keeps versions stable.
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T003` publish evidence package and runbook snippet.
- [IN_PROGRESS] `CAM-MILESTONES-V1.1-P02-T004` remove global milestones DELETE from bulk sync path.
- [DONE] `CAM-MILESTONES-V1.1-P02-T004` remove global milestones DELETE from bulk sync path.
- [DONE] `CAM-MILESTONES-V1.1-P04-T001` migration utility with fallback source (`dtm_task_milestones` -> `raw_payload`).
- [DONE] `CAM-MILESTONES-V1.1-P04-T002` post-migration verification sample + evidence.
- [DONE] `CAM-MILESTONES-V1.1-P05-T001` unit tests for safe bulk replace scope.
- [DONE] `CAM-MILESTONES-V1.1-P05-T003` smoke + evidence closeout.
- [DONE] `CAM-MILESTONES-V1.2-P01-T001` add WRITE_LEGACY_MILESTONES flag.
- [DONE] `CAM-MILESTONES-V1.2-P01-T002` gate legacy milestones writes in sync.
- [DONE] `CAM-MILESTONES-V1.2-P02-T001` builder synthetic start fallback + warnings/log.
- [DONE] `CAM-MILESTONES-V1.2-P02-T002` sync assert on empty milestones_v write.
- [DONE] `CAM-MILESTONES-V1.2-P03-T001` reorder version bump flow for best-effort consistency.
- [DONE] `CAM-MILESTONES-V1.2-P03-T002` guard current_version and milestones_v presence for changed tasks.
- [DONE] `CAM-MILESTONES-V1.2-P04-T001` unit test for synthetic start fallback.
- [DONE] `CAM-MILESTONES-V1.2-P04-T002` unit test for milestones_write_empty failure.
- [DONE] `CAM-MILESTONES-V1.2-P04-T003` unit test for WRITE_LEGACY_MILESTONES=false.
- [DONE] `CAM-MILESTONES-V1.2-P04-T004` publish evidence.

## Done (Latest)
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P01-T001`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P02-T001`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P03-T001`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P04-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P04-T001`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T003`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T002`
- [DONE] `CAM-DBMIG-MILESTONES-V1-P05-T001`
- [DONE] `CAM-MILESTONES-V1.1-P05-T003`
- [DONE] `CAM-MILESTONES-V1.1-P05-T001`
- [DONE] `CAM-MILESTONES-V1.1-P04-T002`
- [DONE] `CAM-MILESTONES-V1.1-P04-T001`
- [DONE] `CAM-MILESTONES-V1.1-P02-T004`
- [DONE] `CAM-MILESTONES-V1.2-P04-T004`
- [DONE] `CAM-MILESTONES-V1.2-P04-T003`
- [DONE] `CAM-MILESTONES-V1.2-P04-T002`
- [DONE] `CAM-MILESTONES-V1.2-P04-T001`
- [DONE] `CAM-MILESTONES-V1.2-P03-T002`
- [DONE] `CAM-MILESTONES-V1.2-P03-T001`
- [DONE] `CAM-MILESTONES-V1.2-P02-T002`
- [DONE] `CAM-MILESTONES-V1.2-P02-T001`
- [DONE] `CAM-MILESTONES-V1.2-P01-T002`
- [DONE] `CAM-MILESTONES-V1.2-P01-T001`
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
- [TODO] Define next campaign scope after `CAM-MILESTONES-V1.2` closeout (owner decision).

# Backlog (CAM IDs)

## Active Campaigns
- `CAM-DOC-REFORM`
- `CAM-DBMIG-MILESTONES-V1`

## Ready Queue
1. `CAM-DBMIG-MILESTONES-V1-P01-T001` - add versioned milestones table in YDB schema.
2. `CAM-DBMIG-MILESTONES-V1-P01-T002` - fix current-version milestone truth rule in docs and repo contract.
3. `CAM-DBMIG-MILESTONES-V1-P01-T003` - define compatibility role of legacy milestones table.
4. `CAM-DBMIG-MILESTONES-V1-P02-T001` - content/timing change path writes milestones for new version.
5. `CAM-DBMIG-MILESTONES-V1-P03-T001` - builder reads milestones strictly by `(task_id, current_version)`.

## Parked / Insert Reserve
- `CAM-DBMIG-MILESTONES-V1-P01-T800` - reserved insert slot.
- `CAM-DBMIG-MILESTONES-V1-P01-T900` - unplanned debt slot.


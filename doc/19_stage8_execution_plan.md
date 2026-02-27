# Stage 8 Execution Plan

## Objective
Build the first read-only web prototype consumer over Stage 7 artifacts with deterministic schema gate and environment-aware artifact source switching.

## Baseline
- Stage 8 estimate baseline: 6 tasks.
- Dynamic tracking rule: update `Done` / `Remaining` in `agile/sprint_current.md` after each completed task.
- Current counter: done `4`, remaining `2`.

## Stage 8 slices (initial)
1. TSK-073 (DTM-70): kickoff and estimate baseline.
2. TSK-074 (DTM-71): prototype data loader + schema gate over read-model artifacts.
3. TSK-075 (DTM-72): static web prototype views (timeline/by-designer/task-details) with filters.
4. TSK-076 (DTM-73): local/cloud source switch for prototype data loader (filesystem/Object Storage).
5. TSK-077: shadow-run execution evidence package for prototype consumer.
6. TSK-078: Stage 8 closeout and next-stage handoff package.

## Delivery rules
- WIP = 1 active execution task.
- Each task follows Jira lifecycle (`V rabote` before changes, evidence comments, `Gotovo` on completion).
- Owner Telegram completion message after each task (`done/remaining`).

## Exit criteria
- Read-only prototype loads Stage 7 artifacts and passes schema gate.
- Prototype supports both local and Object Storage artifact source profiles.
- Shadow-run evidence package is complete and linked in sprint/Jira docs.

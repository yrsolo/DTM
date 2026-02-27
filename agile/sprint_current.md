# Sprint Current

## Sprint Goal
Stabilize Stage 9 serverless delivery and keep process/documentation concise and operational.

## Capacity
1 active task (strict WIP=1).

## Now
- [IN_PROGRESS] none.

## Stage 9 Estimate (Dynamic)
- Baseline estimate: 8 tasks (adjusted after explicit doc-structure refactor slice).
- Done: 6
- Remaining: 2
- Rule: update `Done/Remaining` after each completed Stage 9 task.

## Done
- [DONE] DTM-76 / TSK-079 - main-branch auto-deploy workflow for Yandex Cloud Function.
- [DONE] DTM-77 / TSK-080 - automate `.env` to Lockbox sync + Google key runtime secret source.
- [DONE] DTM-78 / TSK-081 - bind Lockbox env mappings to function + cloud invoke smoke.
- [DONE] DTM-80 / TSK-082 - docs/agile hygiene cleanup and archive normalization.
- [DONE] DTM-81 / TSK-083 - documentation readability refactor (`doc` map + concise backlog format).
- [DONE] DTM-82 / TSK-084 - doc folder restructuring by purpose (`core/ops/governance/stages/archive`).

## Blocked
- [BLOCKED] DTM-83 / TSK-085 - deploy workflow run failed (`No credentials`) after `main` push; requires cloud auth setup decision.

## Next 3-5 Tasks (Groomed)
- [TODO] DTM-83 / TSK-085 - owner-approved `dev -> main` merge and deploy trigger execution.
- [TODO] Stage 9: cloud-profile shadow-run with explicit `PROTOTYPE_*_S3_KEY` pass criteria.
- [TODO] Stage 9: deploy-pipeline consumer contract-regression checks.
- [TODO] Stage 9: deployment smoke checklist for Yandex Cloud Function profile.

## Active Task Files
- `agile/tasks/DTM-83_stage9-main-merge-and-deploy-trigger.md`

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Keep top-level `doc/` minimal and strategy-first.
- Move operational/history/stage-package docs into subfolders to remove numbered clutter.
- Jira remains mandatory lifecycle control plane for all execution tasks.

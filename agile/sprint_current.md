# Sprint Current

## Sprint Goal
Stabilize Stage 9 serverless delivery and normalize delivery documentation so sprint control stays operational and readable.

## Capacity
1 active task (strict WIP=1).

## Now
- [IN_PROGRESS] none.

## Stage 9 Estimate (Dynamic)
- Baseline estimate: 6 tasks (adjusted from 5 after adding explicit docs hygiene slice).
- Done: 4
- Remaining: 2
- Rule: update `Done/Remaining` after each completed Stage 9 task.

## Done
- [DONE] DTM-76 / TSK-079 - main-branch auto-deploy workflow for Yandex Cloud Function.
- [DONE] DTM-77 / TSK-080 - automate `.env` to Lockbox sync + Google key runtime secret source.
- [DONE] DTM-78 / TSK-081 - bind Lockbox env mappings to function + cloud invoke smoke.
- [DONE] DTM-80 / TSK-082 - docs/agile hygiene cleanup and archive normalization.

## Blocked
- [BLOCKED] none.

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 9: cloud-profile shadow-run with explicit `PROTOTYPE_*_S3_KEY` pass criteria.
- [TODO] Stage 9: deploy-pipeline consumer contract-regression checks.
- [TODO] Stage 9: deployment smoke checklist for Yandex Cloud Function profile.

## Active Task Files
- `agile/tasks/DTM-80_docs-agile-hygiene-cleanup.md`

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`

## Notes / Decisions
- Keep `agile/sprint_current.md` as operational board only; do not store full historical logs here.
- Keep evidence history in `agile/archive/*` and task files, with links from current board.
- Jira remains mandatory lifecycle control plane for all execution tasks.

# Sprint Current

## Sprint Goal
Stabilize Stage 9 serverless delivery and keep process/documentation concise and operational.

## Capacity
1 active task (strict WIP=1).

## Now
- [IN_PROGRESS] none.

## Stage 9 Estimate (Dynamic)
- Baseline estimate: 7 tasks (adjusted after explicit docs readability slice).
- Done: 5
- Remaining: 2
- Rule: update `Done/Remaining` after each completed Stage 9 task.

## Done
- [DONE] DTM-76 / TSK-079 - main-branch auto-deploy workflow for Yandex Cloud Function.
- [DONE] DTM-77 / TSK-080 - automate `.env` to Lockbox sync + Google key runtime secret source.
- [DONE] DTM-78 / TSK-081 - bind Lockbox env mappings to function + cloud invoke smoke.
- [DONE] DTM-80 / TSK-082 - docs/agile hygiene cleanup and archive normalization.
- [DONE] DTM-81 / TSK-083 - documentation readability refactor (`doc` map + concise backlog format).

## Blocked
- [BLOCKED] none.

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 9: cloud-profile shadow-run with explicit `PROTOTYPE_*_S3_KEY` pass criteria.
- [TODO] Stage 9: deploy-pipeline consumer contract-regression checks.
- [TODO] Stage 9: deployment smoke checklist for Yandex Cloud Function profile.

## Active Task Files
- `agile/tasks/DTM-81_docs-readability-refactor.md`

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Keep `agile/sprint_current.md` as operational board only.
- Keep `doc/03_reconstruction_backlog.md` concise; move verbose history to `doc/archive/*`.
- Jira remains mandatory lifecycle control plane for all execution tasks.

# Sprint Current

## Sprint Goal
Stabilize Stage 9 serverless delivery and keep process/documentation concise and operational.

## Capacity
1 active task (strict WIP=1).

## Now
- [IN_PROGRESS] Stage 9 closeout summary and Stage 10 handoff prep.

## Stage 9 Estimate (Dynamic)
- Baseline estimate: 11 tasks (expanded with operational closeout slices after runtime incidents).
- Done: 11
- Remaining: 0
- Rule: update `Done/Remaining` after each completed Stage 9 task.

## Done
- [DONE] DTM-76 / TSK-079 - main-branch auto-deploy workflow for Yandex Cloud Function.
- [DONE] DTM-77 / TSK-080 - automate `.env` to Lockbox sync + Google key runtime secret source.
- [DONE] DTM-78 / TSK-081 - bind Lockbox env mappings to function + cloud invoke smoke.
- [DONE] DTM-80 / TSK-082 - docs/agile hygiene cleanup and archive normalization.
- [DONE] DTM-81 / TSK-083 - documentation readability refactor (`doc` map + concise backlog format).
- [DONE] DTM-82 / TSK-084 - doc folder restructuring by purpose (`core/ops/governance/stages/archive`).
- [DONE] DTM-83 / TSK-085 - owner-approved main deploy trigger + credential fallback; deploy run `22500598734` successful.
- [DONE] DTM-84 / TSK-086 - import/runtime Telegram crash fixed for serverless startup; HTTP-body parsing + healthcheck invoke path; deploy run `22501249449` successful, endpoint returns `!HEALTHY!`.
- [DONE] DTM-85 / TSK-087 - deployment smoke checklist published and validated (`healthcheck` + `timer dry-run` evidence), Jira moved to `Готово`.
- [DONE] DTM-86 / TSK-088 - shadow-run cloud gate now supports required `PROTOTYPE_*_S3_KEY` mode with smoke coverage and ops checklist update.
- [DONE] DTM-87 / TSK-089 - deploy workflow now enforces consumer contract-regression smoke checks before cloud deploy.

## Blocked
- [BLOCKED] none.

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 10: kickoff and baseline estimate.
- [TODO] Stage 10: first execution slice grooming.

## Active Task Files
- none (Stage 9 execution queue complete)

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Keep top-level `doc/` minimal and strategy-first.
- Move operational/history/stage-package docs into subfolders to remove numbered clutter.
- Jira remains mandatory lifecycle control plane for all execution tasks.

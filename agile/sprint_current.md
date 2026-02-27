# Sprint Current

## Sprint Goal
Stabilize Stage 9 serverless delivery and keep process/documentation concise and operational.

## Capacity
1 active task (strict WIP=1).

## Now
- [BLOCKED] Stage 9 next slice grooming (post DTM-84 closeout): waiting explicit local-mode waiver or task-system access restore.

## Stage 9 Estimate (Dynamic)
- Baseline estimate: 9 tasks (adjusted after serverless runtime hotfix slice).
- Done: 8
- Remaining: 1
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

## Blocked
- [BLOCKED] Stage 9 execution is paused by process gate (task-system lifecycle unavailable in current runtime); owner escalation sent via `agent/notify_owner.py` on 2026-02-27.

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 9: cloud-profile shadow-run with explicit `PROTOTYPE_*_S3_KEY` pass criteria.
- [TODO] Stage 9: deploy-pipeline consumer contract-regression checks.
- [TODO] Stage 9: deployment smoke checklist for Yandex Cloud Function profile.

## Active Task Files
- `agile/tasks/DTM-84_stage9-serverless-import-token-crash-fix.md`

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Keep top-level `doc/` minimal and strategy-first.
- Move operational/history/stage-package docs into subfolders to remove numbered clutter.
- Jira remains mandatory lifecycle control plane for all execution tasks.

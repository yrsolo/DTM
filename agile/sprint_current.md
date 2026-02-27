# Sprint Current

## Sprint Goal
Kick off Stage 10 with explicit execution baseline and reproducible serverless operations evidence flow.

## Capacity
1 active task (strict WIP=1).

## Now
- [BLOCKED] DTM-92 / TSK-092 - cloud shadow-run evidence run in required-keys mode is blocked by missing cloud keys in runtime contour.

## Stage 10 Estimate (Dynamic)
- Baseline estimate: 6 tasks.
- Done: 4
- Remaining: 2
- Rule: update `Done/Remaining` after each completed Stage 10 task.

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
- [DONE] DTM-88 / TSK-090 - Stage 9 closeout package published and Stage 10 kickoff baseline initialized.
- [DONE] DTM-89 / TSK-091 - rollback drill and recovery notes published for function profile incidents.
- [DONE] DTM-90 / TSK-093 - normalized deploy run evidence report script and smoke check added.
- [DONE] DTM-91 / TSK-094 - owner quickstart checklist published for daily/weekly serverless operations.

## Blocked
- [BLOCKED] DTM-92 - missing required cloud keys for shadow-run (`missing_required_cloud_keys`); owner escalation sent via `agent/notify_owner.py` on 2026-02-27.

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 10: cloud shadow-run evidence run in required keys mode with stored artifact.
- [TODO] Stage 10: closeout and Stage 11 handoff package.

## Active Task Files
- `agile/tasks/DTM-92_stage10-cloud-shadow-run-required-keys.md`

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Keep top-level `doc/` minimal and strategy-first.
- Move operational/history/stage-package docs into subfolders to remove numbered clutter.
- Jira remains mandatory lifecycle control plane for all execution tasks.

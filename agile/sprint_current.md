# Sprint Current

## Sprint Goal
Start Stage 21 delivery contour split: test auto-deploy + manual prod release + API/domain tooling.

## Capacity
1 active execution task (WIP=1).

## Now
- [DONE] DTM-198 - Stage 21 deploy contour split (test auto / prod manual) and API domain scripts.

## Stage 21 Estimate (Dynamic)
- Baseline estimate: 3 tasks.
- Done: 1
- Remaining: 2

## Done (Latest)
- [DONE] DTM-198 - Stage 21 deploy contour split (test auto / prod manual) and API domain scripts.
- [DONE] DTM-197 - Agile folder structure and freshness cleanup.
- [DONE] DTM-196 - Stage 20 closeout and Stage 21 handoff package.
- [DONE] DTM-195 - Stage 20 pre-prod smoke and release-readiness package.
- [DONE] DTM-194 - Stage 20 documentation structure hygiene and stale-tail register.
- [DONE] DTM-193 - Stage 20 doc/agile freshness and consistency audit.
- [DONE] DTM-192 - Stage 20 kickoff and bounded queue.
- [DONE] DTM-191 - Stage 19 closeout and Stage 20 handoff package.

## Blocked
- [BLOCKED] DTM-199 - привязка `dtm-api-test.solofarm.ru` и `dtm-api.solofarm.ru` к API Gateway ожидает `ISSUED` для сертификатов `fpq8qst4i5a7kn626qoi`, `fpq7a9hcft9g03p0g4ro`.

## Next 3-5 Tasks (Groomed)
- [TODO] DTM-199 - Stage 21 API gateway live bind smoke for test/prod domains.
- [TODO] DTM-200 - Stage 21 release runbook (owner step-by-step + rollback).
- [TODO] DTM-201 - Stage 21 closeout and Stage 22 handoff package.

## Active Task Files
- `agile/tasks/stage_20_plus/DTM-198_stage21_deploy-contour-split-test-prod-and-api-domain-tooling.md`

## Task Folder Structure
- `agile/tasks/stage_00_09/` - stage 0-9 execution tasks.
- `agile/tasks/stage_10_19/` - stage 10-19 execution tasks.
- `agile/tasks/stage_20_plus/` - stage 20+ execution tasks.
- `agile/tasks/foundation_misc/` - non-stage/foundation tasks.
- `agile/tasks/active/` - reserved for currently active manual pinning (optional).

## Archive References
- `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- `agile/archive/sprint_current_2026-02-28.stage20_agile_cleanup.md`
- `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`

## Notes / Decisions
- Stage 21 started by explicit owner request for release contour split.
- Main branch keeps auto deploy for test contour only.
- Production deploy remains manual via `workflow_dispatch`.

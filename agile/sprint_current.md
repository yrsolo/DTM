# Sprint Current

## Sprint Goal
Start Stage 21 delivery contour split: test auto-deploy + manual prod release + API/domain tooling.

## Capacity
1 active execution task (WIP=1).

## Now
- [DONE] DTM-217 - Lockbox YDB/rollout resync and required-key verification.
- [DONE] DTM-216 - YDB adapter + rollout switches + lockbox/deploy wiring.
- [DONE] DTM-214 - M5 read-model publication path and build handler wiring.
- [DONE] DTM-213 - M5 minimal read-model builder with grouping and ordering.
- [DONE] DTM-212 - M4 feature-flagged dual-write to JSON operational store.
- [DONE] DTM-211 - M4 minimal JSON operational store (upsert + idempotency test).
- [DONE] DTM-210 - M3 optional runtime hash-gate wiring (feature-flagged).
- [DONE] DTM-209 - M3 hash-basis builder and determinism tests.
- [DONE] DTM-208 - M2-M3 sync handler hash-gate wiring.
- [DONE] DTM-207 - M2 parity smoke for normalize planned dates.
- [DONE] DTM-206 - M2-M3 feature flags and hash-gate smoke.
- [DONE] DTM-205 - M1 normalize fixtures and unit tests.
- [DONE] DTM-204 - Migration blueprint package (docs/*) + M1-M3 scaffolding in src/*.
- [DONE] DTM-203 - API doc endpoint rendered as HTML mini-page and robust gateway path matching.
- [DONE] DTM-202 - Runtime trigger gate + release workflow source-of-truth hotfix.
- [DONE] DTM-200 - Frontend API endpoint and request/response contract doc.
- [DONE] DTM-199 - Stage 21 API gateway live bind smoke for test/prod domains.
- [DONE] DTM-198 - Stage 21 deploy contour split (test auto / prod manual) and API domain scripts.

## Stage 21 Estimate (Dynamic)
- Baseline estimate: 18 tasks.
- Done: 18
- Remaining: 0

## Done (Latest)
- [DONE] DTM-217 - Lockbox YDB/rollout resync and required-key verification.
- [DONE] DTM-216 - YDB adapter + rollout switches + lockbox/deploy wiring.
- [DONE] DTM-214 - M5 read-model publication path and build handler wiring.
- [DONE] DTM-213 - M5 minimal read-model builder with grouping and ordering.
- [DONE] DTM-212 - M4 feature-flagged dual-write to JSON operational store.
- [DONE] DTM-211 - M4 minimal JSON operational store (upsert + idempotency test).
- [DONE] DTM-210 - M3 optional runtime hash-gate wiring (feature-flagged).
- [DONE] DTM-209 - M3 hash-basis builder and determinism tests.
- [DONE] DTM-208 - M2-M3 sync handler hash-gate wiring.
- [DONE] DTM-207 - M2 parity smoke for normalize planned dates.
- [DONE] DTM-206 - M2-M3 feature flags and hash-gate smoke.
- [DONE] DTM-205 - M1 normalize fixtures and unit tests.
- [DONE] DTM-204 - Migration blueprint package (docs/*) + M1-M3 scaffolding in src/*.
- [DONE] DTM-203 - API doc endpoint rendered as HTML mini-page and robust gateway path matching.
- [DONE] DTM-202 - Runtime trigger gate + release workflow source-of-truth hotfix.
- [DONE] DTM-199 - Stage 21 API gateway live bind smoke for test/prod domains.
- [DONE] DTM-200 - Frontend API endpoint and request/response contract doc.
- [DONE] DTM-198 - Stage 21 deploy contour split (test auto / prod manual) and API domain scripts.
- [DONE] DTM-197 - Agile folder structure and freshness cleanup.
- [DONE] DTM-196 - Stage 20 closeout and Stage 21 handoff package.
- [DONE] DTM-195 - Stage 20 pre-prod smoke and release-readiness package.
- [DONE] DTM-194 - Stage 20 documentation structure hygiene and stale-tail register.
- [DONE] DTM-193 - Stage 20 doc/agile freshness and consistency audit.
- [DONE] DTM-192 - Stage 20 kickoff and bounded queue.
- [DONE] DTM-191 - Stage 19 closeout and Stage 20 handoff package.

## Blocked
- [BLOCKED] none.

## Next 3-5 Tasks (Groomed)
- [TODO] DTM-201 - Stage 21 closeout and Stage 22 handoff package.

## Active Task Files
- `agile/tasks/stage_20_plus/DTM-217_stage21_lockbox-ydb-rollout-resync-and-verify.md`

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

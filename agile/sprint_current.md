# Sprint Current

## Sprint Goal
Execute Stage 23 cloud hardening rollout queue from Stage 22 unified baseline.

## Product Blocks (Equal Priority)
- Frontend API
- Sheet Render
- Notifications
- Rule: no block is considered "done for stage" if the other two are unchecked for same contour.

## Capacity
1 active execution task (WIP=1).

## Now
- [DONE] DTM-237 - Canary rollout checklist for source-policy switch + rollback checkpoints.
- [DONE] DTM-236 - Readmodel freshness markers for render/notify cloud parity checks.
- [DONE] DTM-235 - Cloud tri-block smoke automation package.
- [DONE] DTM-234 - Stage 23 kickoff and bounded queue.
- [DONE] DTM-233 - Stage 22 closeout and Stage 23 handoff package.
- [DONE] DTM-232 - Stage 22 tri-block smoke suite from unified query source.
- [DONE] DTM-231 - Stage 22 production runbook for `db_migrate`, forced refresh, rollback and safety gates.
- [DONE] DTM-230 - Source-policy cleanup (`READMODEL_SOURCE`/`NOTIFY_SOURCE`/`RENDER_SOURCE`) with one consumer matrix.
- [DONE] DTM-229 - Unified DB query contract adapter for API/render/notify.
- [DONE] DTM-228 - Stage 22 kickoff and bounded queue.
- [DONE] DTM-201 - Stage 21 closeout and Stage 22 handoff package.
- [DONE] DTM-227 - DB migration v2 finalization: versioning, preflight top-50 gate, forced refresh, and evidence package.
- [DONE] DTM-226 - Improve milestone year inference for legacy rows (`TIMING_YEAR_MODE=legacy|anchors|chain`) with non-regression tests.
- [DONE] DTM-225 - Split test/prod YDB contours across runtime, workflows, and Lockbox payload.
- [DONE] DTM-224 - DB migration v2: cloud smoke passed (`v2` reads YDB readmodel; `v1` dates fixed after hotfix deploy).
- [DONE] DTM-223 - Frontend API v2 + shared task query contract across API/render/reminder; cloud verification passed on test domain.
- [DONE] DTM-222 - Proxy-template route and multi-value query fix for frontend API.
- [DONE] DTM-221 - Frontend API event-shape hardening + Actions requirements split.
- [DONE] DTM-220 - API gateway ANY-method compatibility hotfix.
- [DONE] DTM-218 - API HTTP method fallback hotfix (no-op to frontend route fix).
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

## Stage 23 Estimate (Dynamic)
- Baseline estimate: 6 tasks.
- Done: 4
- Remaining: 2

## Done (Latest)
- [DONE] DTM-237 - Published Stage 23 source-policy canary checklist with rollback checkpoints and production go/no-go inputs (`doc/ops/stage23_source_policy_canary_rollout_checklist.md`).
- [DONE] DTM-236 - Added render/notify readmodel freshness runtime marker (`readmodel_freshness`) with unit tests.
- [DONE] DTM-235 - Added cloud tri-block smoke automation (`agent/stage23_cloud_tri_block_smoke.py`) + test contour evidence artifact.
- [DONE] DTM-234 - Stage 23 kickoff and bounded queue (goal/counters/queue synchronized).
- [DONE] DTM-233 - Published Stage 22 closeout + Stage 23 handoff package (`doc/stages/69`, `doc/stages/70`) and synchronized control-plane docs.
- [DONE] DTM-232 - Added deterministic tri-block parity smoke (`agent/stage22_tri_block_smoke.py`) + unit test; API/render/notify IDs match from one query source.
- [DONE] DTM-231 - Published Stage 22 ops runbook for migrate/forced-refresh/rollback (`doc/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`) and linked from active docs.
- [DONE] DTM-230 - Unified source-policy matrix extracted to `src/services/source_policy.py`; wired into `main.py` and `index.py`; tests+timer smoke passed.
- [DONE] DTM-229 - Shared query adapter layer (`core/task_query_adapter.py`) wired to API v1/v2 + planner + reminder; test and timer smoke passed.
- [DONE] DTM-228 - Stage 22 kickoff and bounded queue (freshness check + bounded execution queue confirmed).
- [DONE] DTM-201 - Stage 21 closeout and Stage 22 handoff package.
- [DONE] DTM-227 - DB migration v2 finalization (`dtm_task_versions`, preflight top-50 + daily full-sync gate, forced refresh no-version-bump, cloud smoke evidence).
- [DONE] DTM-226 - Timing year inference hardening (`legacy|anchors|chain`) + parser/chain regression tests.
- [DONE] DTM-225 - Split test/prod YDB contours (`YDB_*_TEST` / `YDB_*_PROD`) in runtime + CI/CD + Lockbox sync.
- [DONE] DTM-222 - Proxy-template route and multi-value query fix for frontend API.
- [DONE] DTM-223 - Frontend API v2 + shared task query contract; cloud verification passed (`v1/v2/doc` = 200).
- [DONE] DTM-224 - DB migration v2 cloud smoke passed (`v2` readmodel markers confirmed; `v1` date regression fixed).
- [DONE] DTM-221 - Frontend API event-shape hardening + Actions requirements split.
- [DONE] DTM-220 - API gateway ANY-method compatibility hotfix.
- [DONE] DTM-218 - API HTTP method fallback hotfix (no-op to frontend route fix).
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
- none

## Next 3-5 Tasks (Groomed)
- [TODO] DTM-238 - Test-contour operational evidence bundle and production go/no-go inputs.
- [TODO] DTM-239 - Stage 23 closeout and Stage 24 handoff package.

## Tri-Block Readiness Matrix (Test Contour)
- Frontend API: in progress (v1/v2/doc cloud verification passed; pending explicit YDB readmodel-source confirmation in v2 payload).
- Sheet Render: in progress (runtime path works; needs explicit contour smoke evidence and timestamp check).
- Notifications: in progress (delivery logic works; needs contour smoke evidence under current rollout switches).

## Active Task Files
- `agile/tasks/stage_20_plus/DTM-236_stage23_readmodel-freshness-markers-render-notify.md`
- `agile/tasks/stage_20_plus/DTM-235_stage23_cloud-tri-block-smoke-automation-package.md`
- `agile/tasks/stage_20_plus/DTM-234_stage23-kickoff-and-bounded-queue.md`
- `agile/tasks/stage_20_plus/DTM-233_stage22-closeout-and-stage23-handoff.md`
- `agile/tasks/stage_20_plus/DTM-232_stage22_tri-block-smoke-suite-unified-query-source.md`
- `agile/tasks/stage_20_plus/DTM-231_stage22_prod-runbook-db-migrate-force-refresh-rollback.md`
- `agile/tasks/stage_20_plus/DTM-230_stage22_source-policy-cleanup-matrix.md`
- `agile/tasks/stage_20_plus/DTM-229_stage22_unified-db-query-contract-adapter.md`
- `agile/tasks/stage_20_plus/DTM-228_stage22-kickoff-and-bounded-queue.md`
- `agile/tasks/stage_20_plus/DTM-201_stage21-closeout-and-stage22-handoff.md`
- `agile/tasks/stage_20_plus/DTM-227_stage21_db-migration-v2-finalization.md`
- `agile/tasks/stage_20_plus/DTM-224_stage21_db-migration-v2-operational-and-readmodel-store.md`
- `agile/tasks/stage_20_plus/DTM-225_stage21_split-test-prod-ydb-contours.md`
- `agile/tasks/stage_20_plus/DTM-226_stage21_timing-year-inference-hardening.md`

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
- Runtime source switches are set to YDB contour (`STORE_MODE=ydb_primary`, `READMODEL_SOURCE=ydb`, `NOTIFY_SOURCE=ydb`, `RENDER_SOURCE=ydb`) for validation cycle.

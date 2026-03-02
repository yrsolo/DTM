# Sprint Current

## Sprint Goal
Start Stage 21 delivery contour split: test auto-deploy + manual prod release + API/domain tooling.

## Product Blocks (Equal Priority)
- Frontend API
- Sheet Render
- Notifications
- Rule: no block is considered "done for stage" if the other two are unchecked for same contour.

## Capacity
1 active execution task (WIP=1).

## Now
- [BLOCKED] DTM-223 - Frontend API v2 + shared task query contract across API/render/reminder done in code; cloud verification pending manual test deploy.
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

## Stage 21 Estimate (Dynamic)
- Baseline estimate: 23 tasks.
- Done: 22
- Remaining: 1

## Done (Latest)
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
- [BLOCKED] DTM-219 - test contour deploy verification blocked: local token cannot trigger GitHub workflow (`403 workflow_dispatch`), owner must run workflow manually.
- [BLOCKED] DTM-220 - cloud verification pending same manual test deploy.
- [BLOCKED] DTM-221 - cloud verification pending same manual test deploy.
- [BLOCKED] DTM-222 - cloud verification pending same manual test deploy.
- [BLOCKED] DTM-223 - cloud verification pending same manual test deploy.

## Next 3-5 Tasks (Groomed)
- [TODO] DTM-219 - Deploy DTM-218 fix to test contour and verify API domain response.
- [TODO] DTM-220 - Deploy DTM-220 fix to test contour and verify API domain response.
- [TODO] DTM-221 - Deploy DTM-221 fix to test contour and verify API domain response.
- [TODO] DTM-222 - Deploy DTM-222 fix to test contour and verify API domain response.
- [TODO] DTM-223 - Run cloud verification for v1/v2 endpoints after test deploy (`git_ref=dev`).
- [TODO] DTM-201 - Stage 21 closeout and Stage 22 handoff package.

## Tri-Block Readiness Matrix (Test Contour)
- Frontend API: in progress (v2 contract + routing ready in `dev`, cloud verification pending deploy).
- Sheet Render: in progress (runtime path works; needs explicit contour smoke evidence and timestamp check).
- Notifications: in progress (delivery logic works; needs contour smoke evidence under current rollout switches).

## Active Task Files
- `agile/tasks/stage_20_plus/DTM-223_stage21_frontend-api-v2-contract-and-routing-hardening.md`

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

# DTM-168: Stage 15 deploy readiness wait-gate

## Context
- Cloud deploy is asynchronous; manual timing causes false smoke runs.

## Goal
- Add programmatic wait for latest deploy completion before live smoke.

## Non-goals
- CI workflow rewrite.

## Plan
1. Add deploy polling via GitHub Actions API.
2. Expose timeout/poll controls in CLI.
3. Print stable readiness evidence.

## Checklist (DoD)
- [x] `--wait-deploy` implemented.
- [x] Latest run status polling works.
- [x] Success/failure timeout paths explicit.

## Work log
- 2026-02-28: Added wait-gate logic in `agent/cloud_render_freshness_smoke.py`.
- 2026-02-28: Validated with latest successful run id evidence.

## Links
- `agent/cloud_render_freshness_smoke.py`
- `doc/stages/44_stage15_deploy_readiness_and_render_freshness_guard.md`
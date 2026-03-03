# DTM-237: Canary rollout checklist for source-policy switch and rollback checkpoints

## Context
- Stage 23 requires controlled rollout from test contour evidence to production decision.
- Source policy switches (`READMODEL_SOURCE`, `NOTIFY_SOURCE`, `RENDER_SOURCE`) can affect all three product blocks.
- Existing Stage 22 runbook covers migrate/refresh/rollback, but not explicit canary gate sequence for Stage 23.

## Goal
- Publish a canary checklist that defines pre-checks, switch order, rollback points, and go/no-go criteria.
- Bind checklist to current cloud smoke evidence path so rollout steps are executable.

## Non-goals
- No runtime behavior changes.
- No source-policy value changes in production.

## Plan
1. Create Stage 23 canary rollout runbook for source-policy switch.
2. Link checklist from README and active stage plan context.
3. Synchronize sprint/task counters and context trust registry.
4. Capture cloud smoke evidence command output as execution proof.

## Checklist (DoD)
- [x] Stage 23 canary/rollback checklist published in `doc/ops`.
- [x] Checklist has explicit pre-checks, switch sequence, rollback sequence, and go/no-go matrix.
- [x] README links to the new checklist.
- [x] Stage 23 counters synchronized in sprint and stage plan docs.
- [x] Cloud tri-block smoke command run captured as evidence.

## Work log
- 2026-03-03: Published `doc/ops/stage23_source_policy_canary_rollout_checklist.md`.
- 2026-03-03: Linked checklist in `README.md` deployment/runbook section.
- 2026-03-03: Synced Stage 23 counters (`done=4`, `remaining=2`) in `agile/sprint_current.md` and `doc/stages/70_stage23_execution_plan.md`.
- 2026-03-03: Added trust/evidence row for DTM-237 in `agile/context_registry.md`.
- 2026-03-03: Cloud smoke evidence captured:
  - `.venv\\Scripts\\python.exe agent\\stage23_cloud_tri_block_smoke.py --function-url https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba --api-base https://dtm-api-test.solofarm.ru --timeout 180 --output-file artifacts/tmp/stage23_canary_precheck.json`
  - `stage23_cloud_tri_block_smoke_ok=true`

## Links
- Runbook: `doc/ops/stage23_source_policy_canary_rollout_checklist.md`
- Stage plan: `doc/stages/70_stage23_execution_plan.md`

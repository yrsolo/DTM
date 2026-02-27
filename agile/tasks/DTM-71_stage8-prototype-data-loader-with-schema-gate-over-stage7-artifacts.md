# DTM-71: TSK-074 Stage 8 prototype data loader with schema gate over Stage 7 artifacts

## Context
- Stage 8 kickoff completed with execution plan and queue.
- Stage 7 artifacts are available: `read_model`, `schema_snapshot`, `fixture_bundle`.

## Goal
- Implement reusable prototype payload loader with schema gate.
- Support both `filesystem` and `object_storage` source modes.

## Non-goals
- No UI rendering in this task.
- No production deployment changes.

## Plan
1. Add `web_prototype` loader module.
2. Add CLI utility for payload loading and summary output.
3. Add deterministic smoke script for schema-gate behavior.
4. Sync Stage 8 docs and counters.

## Checklist (DoD)
- [x] Loader module added.
- [x] Schema gate is enforced.
- [x] Filesystem/Object Storage source modes are supported.
- [x] Smoke checks pass.
- [x] Sprint/context/backlog/docs aligned.

## Work log
- 2026-02-27: DTM-71 created and moved to `V rabote`.
- 2026-02-27: Added `web_prototype/loader.py`, `agent/load_prototype_payload.py`, and `agent/prototype_loader_smoke.py`.
- 2026-02-27: Updated Stage 8 docs/counters (`done 2 / remaining 4`).

## Links
- Jira: DTM-71
- Stage plan: `doc/19_stage8_execution_plan.md`

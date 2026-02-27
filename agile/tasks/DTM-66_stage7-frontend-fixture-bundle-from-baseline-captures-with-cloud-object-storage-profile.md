# DTM-66: TSK-069 Stage 7 frontend fixture bundle from baseline captures with cloud Object Storage profile

## Context
- Stage 7 already has `read_model.json` + `schema_snapshot.json`.
- Frontend integration needs reduced stable sample payload from baseline captures.
- Serverless contour requires cloud-compatible artifact export path.

## Goal
- Add deterministic fixture bundle artifact for frontend integration checks.
- Keep cloud profile path available through Object Storage key export.

## Non-goals
- No UI rendering implementation.
- No mandatory auto-upload in local dev path.

## Plan
1. Add fixture bundle builder from read-model + schema snapshot.
2. Add helper script to build fixture bundle from baseline directories.
3. Extend baseline helper to emit fixture bundle.
4. Align docs and stage counters.

## Checklist (DoD)
- [x] Fixture bundle builder added.
- [x] Helper script exists (`agent/build_fixture_bundle.py`).
- [x] Baseline capture emits `fixture_bundle.json`.
- [x] Docs/sprint/context updated.
- [x] Smoke checks passed.

## Work log
- 2026-02-27: DTM-66 created and moved to `V rabote`.
- 2026-02-27: Added `core/fixture_bundle.py` and `agent/build_fixture_bundle.py`.
- 2026-02-27: Baseline helper extended to generate `fixture_bundle.json`.
- 2026-02-27: Added smoke `agent/fixture_bundle_smoke.py` and updated Stage 7 docs (`done 4 / remaining 3`).

## Links
- Jira: DTM-66
- Stage plan: `doc/14_stage7_execution_plan.md`
- Policy: `doc/15_stage7_read_model_consumer_policy.md`

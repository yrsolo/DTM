# DTM-64: TSK-067 Stage 7 read-model consumer compatibility policy and serverless artifact storage contour

## Context
- Stage 7 started with initial plan in `doc/14_stage7_execution_plan.md`.
- Existing artifact flow is local filesystem-oriented (`artifacts/...`) and is not primary-suitable for serverless cloud runtime.
- Production target runtime is Yandex Cloud function with Object Storage available for persistent artifacts.

## Goal
- Define explicit read-model consumer compatibility policy.
- Define serverless-ready artifact storage contour: Object Storage primary, local filesystem dev-only.

## Non-goals
- No implementation of Object Storage upload adapter in this task.
- No schema snapshot or fixture generator implementation yet (next Stage 7 slices).

## Plan
1. Verify freshness across Stage 7 sources (`doc/14`, `doc/04`, `doc/02`, `README`).
2. Add dedicated policy doc covering compatibility and storage contour.
3. Align Stage 7 execution plan and operational docs to this policy.
4. Sync sprint/Jira/task records and smoke-check entrypoint docs.

## Checklist (DoD)
- [x] Jira lifecycle completed (`V rabote` -> `Gotovo`) with evidence comments.
- [x] Policy doc added with compatibility rules and storage contour.
- [x] Stage 7 plan updated with cloud-storage-aware wording.
- [x] Baseline/README docs aligned with serverless storage note.
- [x] Sprint board updated (`done/remaining`, done list, next tasks wording).
- [x] Freshness/trust evidence recorded in context registry.

## Work log
- 2026-02-27: Created DTM-64 and moved to `V rabote`.
- 2026-02-27: Added `doc/15_stage7_read_model_consumer_policy.md` with compatibility and Object Storage contour policy.
- 2026-02-27: Updated Stage 7/smoke docs and sprint records for serverless artifact handling.
- 2026-02-27: Smoke checks passed: `.venv\Scripts\python.exe local_run.py --help`, `.venv\Scripts\python.exe agent\capture_baseline.py --help`.

## Links
- Jira: DTM-64
- Sprint: `agile/sprint_current.md`
- Policy: `doc/15_stage7_read_model_consumer_policy.md`

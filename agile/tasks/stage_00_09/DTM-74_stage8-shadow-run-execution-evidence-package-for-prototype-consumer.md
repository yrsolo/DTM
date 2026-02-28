# DTM-74: TSK-077 Stage 8 shadow-run execution evidence package for prototype consumer

## Context
- Stage 8 prototype loader/UI/source-switch are completed (`DTM-71..DTM-73`).
- Stage 8 requires execution-grade shadow-run evidence package over baseline artifacts.

## Goal
- Add reproducible command that builds shadow-run evidence package with command logs and checklist result.
- Confirm local profile path and optional cloud path behavior are captured in one artifact.

## Non-goals
- No production deployment or live user traffic switch.
- No write-back path changes to Sheets/production endpoints.

## Plan
1. Add Stage 8 shadow-run evidence builder script.
2. Add dedicated smoke script for builder output contract.
3. Run evidence builder and capture artifact path.
4. Sync sprint/stage/docs counters.

## Checklist (DoD)
- [x] `agent/stage8_shadow_run_evidence.py` added.
- [x] `agent/stage8_shadow_run_evidence_smoke.py` passes.
- [x] Shadow-run evidence artifact generated from current baseline.
- [x] Sprint/docs synced (`done 5 / remaining 1`).

## Work log
- 2026-02-27: DTM-74 created and moved to `V rabote`.
- 2026-02-27: Added shadow-run evidence builder + smoke and generated evidence artifact bundle.
- 2026-02-27: Final evidence artifact generated: `artifacts/shadow_run_stage8/20260227T161720Z_dtm74_final/shadow_run_evidence.json` (cloud check skipped due missing `PROTOTYPE_*_S3_KEY` env keys in current shell run).
- 2026-02-27: Synced Stage 8 docs/counters and prepared Jira closeout comment.

## Links
- Jira: DTM-74
- Stage plan: `doc/stages/19_stage8_execution_plan.md`

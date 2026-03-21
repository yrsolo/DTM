# Stage 23 Source-Policy Canary Rollout Checklist

## Scope
- Controlled switch validation for:
  - `READMODEL_SOURCE`
  - `NOTIFY_SOURCE`
  - `RENDER_SOURCE`
- Contours:
  - test (`dtm-api-test.solofarm.ru`, test function)
  - production (manual release contour)

## Preconditions
1. Latest deploy in test contour is green.
2. Lockbox payload contains expected source-policy keys and YDB contour keys.
3. Stage 23 cloud smoke helper is available:
   - `.venv\Scripts\python.exe agent\stage23_cloud_tri_block_smoke.py ...`

## Canary Gate 0: Pre-switch checks (test contour)
1. Run contract smoke:
   - `.venv\Scripts\python.exe agent\read_model_contract_compat_smoke.py`
   - `.venv\Scripts\python.exe agent\schema_snapshot_smoke.py`
2. Run tri-block cloud smoke:
   - `.venv\Scripts\python.exe agent\stage23_cloud_tri_block_smoke.py --function-url <test_function_url> --api-base https://dtm-api-test.solofarm.ru --output-file artifacts/tmp/stage23_canary_precheck.json`
3. Local timer smoke:
   - `cmd /c run_timer.cmd`

Proceed only if all checks pass.

## Canary Gate 1: Source-policy switch validation (test contour)
1. Confirm runtime switches are intended values for test contour.
2. Invoke test function in `timer` mode and collect logs.
3. Verify markers:
   - `api_v2` payload includes `meta.readmodelSource`.
   - runtime logs include `readmodel_freshness=...` for render/notify contour checks.
4. Re-run tri-block cloud smoke and compare with Gate 0 output.

## Canary Gate 2: Rollback readiness checkpoint
Rollback trigger conditions (any one):
- API v1/v2 response contract mismatch.
- `run_timer.cmd` or cloud timer invoke fails.
- repeated transient YDB failures causing unstable run outcome.
- render/notify freshness marker absent when YDB contour is expected.

Rollback actions:
1. Revert source-policy switches to known stable values:
   - `READMODEL_SOURCE=legacy`
   - `NOTIFY_SOURCE=legacy`
   - `RENDER_SOURCE=legacy`
2. Keep store in safe mode (`STORE_MODE=dual_write` or known stable value).
3. Redeploy contour.
4. Re-run Gate 0 checks and record evidence.

## Production Go/No-Go Inputs
- Required before prod canary:
  - latest test contour Gate 0 + Gate 1 evidence files,
  - explicit rollback rehearsal result from Gate 2 checklist,
  - no unresolved blockers in `work/now/tasks.md`.
- No-Go if:
  - any tri-block smoke check fails,
  - evidence missing for API/render/notify parity,
  - rollback path not validated.

## Evidence Artifacts
- `artifacts/tmp/stage23_canary_precheck.json`
- `artifacts/tmp/stage23_canary_postswitch.json` (when Gate 1 runs)
- legacy task log (archive):
  - `archive/work/agile_legacy/legacy_2026-03-03/task_cards_legacy/stage_20_plus/DTM-237_stage23_canary-rollout-checklist-source-policy-switch.md`
- active campaign evidence:
  - `work/roadmap/campaigns/CAM-DBMIG-MILESTONES-V1/evidence.md`



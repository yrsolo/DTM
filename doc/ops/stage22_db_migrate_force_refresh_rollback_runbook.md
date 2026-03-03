# Stage 22 DB Migrate / Force Refresh / Rollback Runbook

## Scope
- Test and production contours for YDB-backed runtime.
- Operations covered:
  - one-time DB schema init (`db_migrate`),
  - controlled forced refresh,
  - rollback to last stable source-policy contour.

## Preconditions
- GitHub Actions variables/secrets are synced (function ids, Lockbox id, contour env keys).
- Runtime service account has required YDB and Lockbox permissions.
- Latest deploy workflows are green on `dev`/`main` test contour.

## Safety Gates (must pass before change)
1. Contract smoke:
   - `python agent/read_model_contract_compat_smoke.py`
   - `python agent/schema_snapshot_smoke.py`
2. Local runtime smoke:
   - `cmd /c run_timer.cmd`
3. YDB read path smoke (optional but recommended):
   - `.venv\Scripts\python.exe -m unittest tests.api.test_frontend_api_routing -v`

If any gate fails: do not continue with migrate/refresh.

## Procedure A: One-time DB migrate
1. Trigger function with explicit mode:
   - `RUN_MODE=db_migrate` (or event `mode=db_migrate`).
2. Expected logs:
   - `db_migrate_done=true`
3. Verify no planner run happened:
   - no render/reminder runtime markers in same invoke.

## Procedure B: Forced refresh (no version bump)
1. Trigger function with:
   - `mode=sync-only`
   - `force_refresh=1`
2. Expected logs:
   - `migration_operational_sync ... forced_refresh=True`
   - readmodel build marker with updated `generated_at`.
3. Verify behavior:
   - data/readmodel refreshed,
   - existing task versions are not incremented by forced refresh mode.

## Procedure C: Rollback
Use when YDB contour is unstable or smoke fails after deployment.

1. Switch source-policy to stable legacy contour:
   - `READMODEL_SOURCE=legacy`
   - `NOTIFY_SOURCE=legacy`
   - `RENDER_SOURCE=legacy`
2. Keep store safe:
   - `STORE_MODE=dual_write` (or previous known-good mode).
3. Redeploy target contour (test first, then prod if needed).
4. Re-run smoke:
   - endpoint API check (`/api/v1/frontend`, `/api/v2/frontend/doc`)
   - `run_timer.cmd`
5. Record rollback evidence in sprint/task logs.

## Post-checklist
- [ ] API v1/v2 endpoints respond as expected.
- [ ] Timer run completes without runtime errors.
- [ ] No uncontrolled `RESOURCE_EXHAUSTED` storm in logs.
- [ ] Current contour flags are documented in sprint notes.

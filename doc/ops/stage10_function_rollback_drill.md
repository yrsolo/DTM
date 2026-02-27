# Stage 10 Function Rollback Drill And Recovery Notes

## Goal
Define a repeatable rollback procedure when latest function deploy version is unhealthy.

## Trigger Conditions
- Smoke check returns `!!!EGGORR!!!` on latest version.
- Deploy workflow is green, but runtime behavior regressed.
- Critical cost/risk signal from reminder or timer path after release.

## Rollback Drill Steps
1. Identify last known good version in Yandex Cloud Function version list.
2. Update function traffic/active version to that known good version.
3. Re-run smoke checks:
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer --dry-run --mock-external`
4. Confirm logs no longer contain new regression signature.
5. Freeze new deploys until root cause note is added to Jira task.

## Recovery Notes Template
- Incident timestamp (UTC):
- Failed deploy run id:
- Rolled back to function version:
- Smoke results after rollback:
- Root cause hypothesis:
- Follow-up task key:

## Prevention Checklist
- Keep deploy contract smoke checks green before release.
- Keep `YC_LOCKBOX_SECRET_ID` and runtime service account configuration immutable per environment.
- Use Stage 9 deployment smoke checklist on every main deploy.

# Stage 9 Deployment Smoke Checklist (Yandex Cloud Function)

## Purpose
Fast post-deploy verification for serverless runtime profile after each `main` auto-deploy.

## Preconditions
- Latest GitHub workflow `Deploy Yandex Cloud Function (main)` is `success`.
- Function endpoint URL is known (`YC_FUNCTION_URL` or explicit `--url`).
- Lockbox mappings and runtime service account are already configured.

## Smoke Steps
1. Health endpoint (loader/runtime check only):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
   - Expected: `status_code=200`, body `!HEALTHY!`.
2. Timer pipeline dry run (no external side effects):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer --dry-run --mock-external`
   - Expected: `status_code=200`, body `!GOOD!`.
3. Timer pipeline live run (real sheet update path):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer`
   - Expected: `status_code=200`, body `!GOOD!`.
4. Cloud-profile shadow-run gate (Object Storage keys required):
   - `.venv\Scripts\python.exe agent\stage8_shadow_run_evidence.py --require-cloud-keys`
   - Expected: `stage8_shadow_run_evidence_ok` and no `missing_required_cloud_keys`.

## Failure Triage
- `!!!EGGORR!!!` + `FileNotFoundError key/...json` in logs:
  - Lockbox/Google key mapping is missing for this function version.
- Deploy failure `service account ... is not available`:
  - Invalid runtime service account id or account not available in target folder.
- Deploy failure `Broken reference to Lockbox Secret`:
  - Invalid `YC_LOCKBOX_SECRET_ID` value (must be secret id, not name).

## Evidence Template
- Deploy run id: `<github_run_id>`
- Smoke command 1 result: `<status/body>`
- Smoke command 2 result: `<status/body>`
- Smoke command 3 result: `<status/body>`
- Notes: `<observed warnings/errors>`
- Normalized run evidence report:
  - `.venv\Scripts\python.exe agent\deploy_run_evidence_report.py --per-page 1 --output-file artifacts/tmp/deploy_run_evidence.json`

# Stage 9 Deployment Smoke Checklist (Yandex Cloud Function)

## Purpose
Fast post-deploy verification for serverless runtime profile after each `main` auto-deploy.

## Preconditions
- Latest GitHub workflow `Deploy Yandex Cloud Function (main)` is `success`.
- Function endpoint URL is known (`YC_FUNCTION_URL` or explicit `--url`).
- Lockbox mappings and runtime service account are already configured.

## Smoke Steps
1. Deploy readiness gate (optional but recommended right after push to `main`):
   - `.venv\Scripts\python.exe agent\cloud_render_freshness_smoke.py --wait-deploy --url <function_url> --mode timer --dry-run --mock-external --spreadsheet-name "<target_spreadsheet>" --worksheet-name "Задачи" --max-age-minutes 120 --post-invoke-wait-sec 0`
   - Expected: `deploy_ready run_id=<...>`.
2. Health endpoint (loader/runtime check only):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
   - Expected: `status_code=200`, body `!HEALTHY!`.
3. Timer pipeline dry run (no external side effects):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer --dry-run --mock-external`
   - Expected: `status_code=200`, body `!GOOD!`.
4. Timer pipeline live run (real sheet update path):
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer`
   - Expected: `status_code=200`, body `!GOOD!`.
5. Render freshness criterion (diagram really updated in Google Sheet):
   - `.venv\Scripts\python.exe agent\cloud_render_freshness_smoke.py --url <function_url> --mode timer --spreadsheet-name "<target_spreadsheet>" --worksheet-name "Задачи" --timestamp-cell A1 --max-age-minutes 20 --post-invoke-wait-sec 12`
   - Expected:
     - `cloud_render_freshness_smoke_ok`
     - `corner_age_minutes <= 20`
     - corner timestamp is close to current time (not stale like "2 hours ago").
6. Cloud-profile shadow-run gate (Object Storage keys required):
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
- Smoke command 4 result: `<freshness ok + age minutes>`
- Notes: `<observed warnings/errors>`
- Normalized run evidence report:
  - `.venv\Scripts\python.exe agent\deploy_run_evidence_report.py --per-page 1 --output-file artifacts/tmp/deploy_run_evidence.json`

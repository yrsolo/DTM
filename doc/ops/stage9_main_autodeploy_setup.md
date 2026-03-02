# Stage 9+: Serverless Deploy Setup (Test/Prod Split)

## Goal
Use two separate cloud functions and domains:
- regular deploys (`push` to `main`) go to test contour,
- production deploy is manual and goes to prod contour.

## Workflows
- Test auto-deploy: `.github/workflows/deploy_yc_function_main.yml`
  - trigger: `push` to `main`
  - function: `YC_CLOUD_FUNCTION_NAME`
  - runtime env: `ENV=test`
  - api domain env: `API_DOMAIN_TEST`
- Prod manual release: `.github/workflows/release_yc_function_prod.yml`
  - trigger: `workflow_dispatch`
  - function: `YC_CLOUD_FUNCTION_PROD_NAME`
  - runtime env: `ENV=prod`
  - api domain env: `API_DOMAIN_PROD`

## Required GitHub Variables/Secrets
Set in `Settings -> Secrets and variables -> Actions`:
- `YC_FOLDER_ID`
- `YC_SERVICE_ACCOUNT_ID` or `YC_RUNTIME_SERVICE_ACCOUNT_ID`
- `YC_LOCKBOX_SECRET_ID`
- `YC_CLOUD_FUNCTION_NAME`
- `YC_CLOUD_FUNCTION_PROD_NAME`
- `YC_CLOUD_FUNCTION_PROD_ID`
- `SOURCE_SHEET_NAME`
- `API_DOMAIN_TEST`
- `API_DOMAIN_PROD`
- `WEB_DOMAIN` (recommended)
- `YC_SA_JSON_CREDENTIALS` (secret)

## Lockbox sync for release
- Full sync from local `.env`:
  - `.venv\Scripts\python.exe agent\sync_lockbox_from_env.py --secret-name DTM`
- Production prep helper (validates required prod keys and then syncs):
  - `.venv\Scripts\python.exe agent\prepare_prod_release.py`
  - required keys:
    - `TARGET_SHEET_NAME_PROD`
    - `YC_CLOUD_FUNCTION_PROD_NAME`
    - `YC_CLOUD_FUNCTION_PROD_ID`
    - `WEB_DOMAIN`
    - `API_DOMAIN_PROD`
    - `API_DOMAIN_TEST`

## API Gateway and custom domains
Use local helper script (one command per contour):
- Test contour:
  - `.venv\Scripts\python.exe agent\deploy_api_gateway_domain.py --mode test`
- Prod contour:
  - `.venv\Scripts\python.exe agent\deploy_api_gateway_domain.py --mode prod`

Script inputs come from `.env`/environment:
- Test:
  - `YC_API_GATEWAY_TEST_NAME` (optional; default `dtm-api-test`)
  - `YC_API_GATEWAY_TEST_ID` (optional; if set, updates existing gateway)
  - `YC_API_CERTIFICATE_ID_TEST` (required for domain bind)
  - `API_DOMAIN_TEST`
- Prod:
  - `YC_API_GATEWAY_PROD_NAME` (optional; default `dtm-api-prod`)
  - `YC_API_GATEWAY_PROD_ID` (optional; if set, updates existing gateway)
  - `YC_API_CERTIFICATE_ID_PROD` (required for domain bind)
  - `API_DOMAIN_PROD`

## Smoke checks
1. Push small commit to `main` and verify test workflow is green.
2. Run manual prod workflow and verify release run is green.
3. Verify both function versions exist in cloud console.
4. Verify direct function healthcheck:
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
5. Verify API gateway endpoint/domain response for each contour.

## Notes
- Workflows explicitly prevent bare deploys by requiring lockbox id and runtime service account.
- Production release remains manual by design (`workflow_dispatch` only).
- Runtime service account must have `lockbox.payloadViewer` on secret `YC_LOCKBOX_SECRET_ID`.

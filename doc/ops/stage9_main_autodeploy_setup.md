# Stage 9: Main Auto-Deploy Setup (Yandex Cloud Function)

## Goal
Deploy a new Cloud Function version automatically on every `push` to `main`.

## Implemented CI workflow
- File: `.github/workflows/deploy_yc_function_main.yml`
- Trigger: `push` to `main`
- Deploy action: `yc-actions/yc-sls-function@v4`
- Default runtime contour:
  - `runtime=python311`
  - `entrypoint=index.handler`
  - `memory=512Mb`
  - `execution-timeout=60s`

## What owner must provide (GitHub Repository Variables)
Set these in `Settings -> Secrets and variables -> Actions -> Variables`:
- `YC_FOLDER_ID`
- `YC_SERVICE_ACCOUNT_ID`
- `YC_CLOUD_FUNCTION_NAME`

Optional overrides:
- `YC_FUNCTION_ENTRYPOINT` (default: `index.handler`)
- `YC_FUNCTION_RUNTIME` (default: `python311`)
- `YC_FUNCTION_MEMORY` (default: `512Mb`)
- `YC_FUNCTION_TIMEOUT` (default: `60s`)

## One-time setup in Yandex Cloud
1. Create/choose service account for GitHub deploys.
2. Grant minimal roles required for function version deployment in target folder.
3. Configure Workload Identity Federation for GitHub repository and bind it to the service account.

## Smoke check after first deploy
1. Push a tiny commit to `main`.
2. Verify GitHub Actions job `Deploy Yandex Cloud Function (main)` is green.
3. Verify new function version appears in Yandex Cloud console.
4. Trigger function once and confirm runtime logs are healthy.

## Notes
- Current workflow packages source from repository (Python modules and docs) and excludes secrets, artifacts, notebooks, and local virtualenv.
- If runtime requires additional environment variables in function configuration, keep them managed in Yandex Cloud function settings (or add controlled CI wiring as next task).
- For non-manual secret refresh from local contour, use:
  - `.venv\Scripts\python.exe agent\sync_lockbox_from_env.py --secret-name DTM`
  This command syncs all non-empty `.env` keys and also updates `GOOGLE_KEY_JSON` from local key file as text payload entry.
- After secret sync, publish function version with Lockbox secret mappings (`--secret ... environment-variable=...`) and ensure runtime service account has `lockbox.payloadViewer` on secret `DTM`.

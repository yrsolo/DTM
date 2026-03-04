# Configuration (Current)

Current runtime source of truth: `config/constants.py`, with YAML-backed defaults via `src/config/loader.py`.

Transition scaffold for `CAM-CONFIG-REFORM-V0`:
- `config/runtime.yaml`
- `config/tables.yaml`
- `config/db.yaml`
- `config/llm.yaml`
- `config/mapping.yaml`
- `config/deploy.yaml`
- `src/config/schema.py`
- `src/config/loader.py`
- `src/app/bootstrap.py`

Entrypoints still import `config/constants.py`, but defaults are sourced from YAML.

## Runtime contour
- `ENV` = `dev|test|prod`
- `STRICT_ENV_GUARD` (optional override)

## Domains
- YAML defaults: `config/runtime.yaml` (`web.domain`, `web.api_domain_test`, `web.api_domain_prod`)
- ENV overrides (optional): `WEB_DOMAIN`, `API_DOMAIN_TEST`, `API_DOMAIN_PROD`
- `API_DOMAIN` is derived from `ENV`

## Runtime switches (YAML defaults, ENV overrides optional)
- `DEBUG_HTTP_EVENT`
- `TIMING_YEAR_MODE`
- `STORE_MODE`, `READMODEL_SOURCE`, `NOTIFY_SOURCE`, `RENDER_SOURCE`
- `FORCE_REFRESH`, `READMODEL_TTL_MINUTES`, `PREFLIGHT_TOP_ROWS`, `FULL_SYNC_INTERVAL_HOURS`
- `LEGACY_BLOB_WRITE`, `WRITE_LEGACY_MILESTONES`, `YDB_MIGRATE_ON_START`

API policy note:
- API v1 support is discontinued (owner decision dated 2026-03-04).
- `FRONTEND_API_DEFAULT_VERSION` is removed from active runtime configuration contour.

## YDB
Contour-aware env keys:
- `YDB_ID_TEST`, `YDB_ENDPOINT_TEST`, `YDB_DATABASE_TEST`
- `YDB_ID_PROD`, `YDB_ENDPOINT_PROD`, `YDB_DATABASE_PROD`
- legacy fallback: `YDB_ID`, `YDB_ENDPOINT`, `YDB_DATABASE`

Backoff tuning:
- `YDB_EXHAUSTED_MAX_ATTEMPTS`
- `YDB_EXHAUSTED_BASE_BACKOFF_SECONDS`
- `YDB_EXHAUSTED_MAX_BACKOFF_SECONDS`
- `YDB_EXHAUSTED_JITTER_RATIO`

## Google Sheets
Google key resolution (priority):
1. `GOOGLE_KEY_JSON_PATH`
2. `GOOGLE_KEY_JSON_B64`
3. `GOOGLE_KEY_JSON`
4. fallback repo file path

Sheet names and column maps are in `config/tables.yaml`.
Optional overrides via ENV: `SOURCE_SHEET_NAME`, `TARGET_SHEET_NAME`.

## Object Storage
Defaults are in `config/db.yaml` (`object_storage.endpoint_url_default`, `object_storage.bucket_default`).
Optional overrides: `S3_ENDPOINT_URL`, `S3_BUCKET`.
Credentials stay in ENV/secret storage: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

## LLM
Provider/model defaults are in `config/llm.yaml`.
Secrets stay in ENV/secret storage:
- `OPENAI_TOKEN`, `ORG_TOKEN`
- `GOOGLE_LLM_API_KEY`
- `YANDEX_LLM_API_KEY`

## Telegram
- `TG_TOKEN` (secret)
- `DEFAULT_CHAT_ID` (optional override)
- `TG_BOT_USERNAME` (optional override)

## Deploy workflows
GitHub Actions now read non-secret deploy defaults from `config/deploy.yaml`.
Critical secrets remain in GitHub/Lockbox.

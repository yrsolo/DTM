# Configuration (Current)

## Source of truth
Typed config is loaded through:
- `src/config/schema.py`
- `src/config/loader.py`
- composed in `src/app/bootstrap.py`

Primary config files:
- `config/runtime.yaml`
- `config/tables.yaml`
- `config/db.yaml`
- `config/llm.yaml`
- `config/mapping.yaml`
- `config/deploy.yaml`

## Runtime contour
- `runtime.env`: `dev|test|prod`
- `runtime.timezone`: default `Europe/Moscow`
- `runtime.snapshot_engine.*`: snapshot/Object Storage settings
- `runtime.queue.*`: Yandex Message Queue settings
- `runtime.telegram.*`: webhook and sender settings
- `runtime.notify.*`: reminder retry/enhancer/test-chat policy
- `runtime.monitoring.*`: Yandex Monitoring backend settings
- `runtime.prometheus.*`: Prometheus-compatible sink settings
- `runtime.grafana.*`: Grafana dashboard/embed metadata
- `runtime.api.auth_trusted_secret_header`: trusted proxy secret header name for browser-facing auth
- `runtime.api.auth_trusted_fallback`: direct/untrusted browser fallback mode (`masked`)
- `runtime.api.auth_mask_dictionary_version`: deterministic masking dictionary version

## Secrets
Secrets stay outside repo config files:
- Google credentials
- Object Storage credentials
- Telegram token
- LLM provider tokens
- Yandex Cloud auth/service secrets
- `YANDEX_PROMETHEUS_API_KEY` / `YMP_API_KEY`
- `GRAFANA_TOKEN`
- `BROWSER_AUTH_PROXY_SECRET`

They are resolved through secret storage / env in loader/bootstrap only.

Current active runtime no longer requires YDB contour secrets:
- no `YDB_ID_*`
- no `YDB_ENDPOINT_*`
- no `YDB_DATABASE_*`

If old migration/backfill utilities still need YDB, they must receive endpoint/database explicitly via their own args or local tooling env, not through active deploy/runtime wiring.

## Object Storage
Used for:
- raw snapshot
- prep snapshot
- people snapshot
- extra metadata
- attachment binaries
- job status/history

## Queue
Queue config defines:
- enabled flag
- queue URLs for test/prod
- status/history prefixes
- endpoint/auth data for live queue introspection

## Deploy workflows
Current workflows:
- `.github/workflows/deploy_yc_function_main.yml` — deploy on push to `test`
- `.github/workflows/release_yc_function_prod.yml` — manual prod release

## Config policy
- no `os.getenv()` outside loader/bootstrap
- services receive typed config objects
- env-based branching belongs in bootstrap/policy selection, not inside core services

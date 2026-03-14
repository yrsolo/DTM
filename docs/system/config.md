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
- `runtime.bottleneck_metrics_level`: `off|stages|debug` profiling policy for detailed bottleneck analytics
- `runtime.metrics_delivery_mode`: `buffered|off` delivery policy for runtime metrics writes
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
- `runtime.api.frontend_response_cache_ttl_minutes`: TTL for default frontend response cache entries
- `runtime.snapshot_engine.prefix_responses`: Object Storage prefix for cached frontend responses

Current profiling policy:
- `off` keeps only baseline runtime metrics
- `stages` emits stage timings/counters for bottleneck analysis
- `debug` emits stage timings plus debug trace details for short investigations

Current metrics delivery policy:
- `buffered` accumulates runtime metrics in memory per request/job and performs one best-effort flush at the end
- `off` disables runtime metrics writes through the main `metrics_client`

Current API metrics policy:
- `runtime.monitoring.emit_api_metrics=false` disables remote/runtime metric emission for `/api` and `/info` hot paths
- in-process traces, `Server-Timing`, and `/info` bottleneck diagnostics stay available

Backward compatibility:
- legacy `runtime.dev_mode_metrics=true` is still treated as `stages` until cleanup removes the old boolean
- `METRICS_DELIVERY_MODE` may override YAML at runtime for quick operator disable/restore

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
Current deploy workflows map `BROWSER_AUTH_PROXY_SECRET` from Lockbox into backend function env for both test and prod contours.

Browser auth secret wiring:
- backend bootstrap reads `BROWSER_AUTH_PROXY_SECRET` in `src/app/bootstrap.py`
- backend trust logic consumes it in `src/entrypoints/http/access_context.py`
- test workflow: `.github/workflows/deploy_yc_function_main.yml`
- prod workflow: `.github/workflows/release_yc_function_prod.yml`
- external auth contour must use the same Lockbox-backed secret value when forwarding `X-DTM-Proxy-Secret`
- operator verification steps live in `docs/system/browser_auth_runbook.md`

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

## People registry
- `config/tables.yaml -> field_maps.people` is the source-of-truth mapping for full people-registry columns.
- secret-only internal route `GET /api/v2/people` reuses `BROWSER_AUTH_PROXY_SECRET` and `runtime.api.auth_trusted_secret_header`.
- people snapshot stores the full normalized registry from sheet `Люди` and is separate from `frontend_v2.entities.people`.

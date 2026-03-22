# Конфигурация

## Source of truth

Typed config загружается через:
- `src/config/schema.py`
- `src/config/loader.py`
- `src/platform/bootstrap.py`

Основные config files:
- `config/runtime.yaml`
- `config/tables.yaml`
- `config/db.yaml`
- `config/llm.yaml`
- `config/mapping.yaml`
- `config/deploy.yaml`

## Runtime contour

- `runtime.env`: `dev|test|prod`
- `runtime.timezone`: по умолчанию `Europe/Moscow`
- `runtime.bottleneck_metrics_level`: `off|stages|debug`
- `runtime.metrics_delivery_mode`: `buffered|off`
- `runtime.snapshot_engine.*`: snapshot/Object Storage settings
- `runtime.queue.*`: queue settings
- `runtime.telegram.*`: webhook и sender settings
- `runtime.notify.*`: reminder delivery settings
- `runtime.monitoring.*`: Monitoring backend settings
- `runtime.prometheus.*`: Prometheus sink settings
- `runtime.grafana.*`: Grafana metadata
- `runtime.api.*`: browser auth, masking и frontend cache settings

## Profiling и metrics policy

`runtime.bottleneck_metrics_level`:
- `off` — только базовые метрики;
- `stages` — stage timings и counters;
- `debug` — stage timings плюс расширенные trace details.

`runtime.metrics_delivery_mode`:
- `buffered` — один best-effort flush в конце request/job;
- `off` — runtime metrics writes выключены.

Для hot paths:
- `runtime.monitoring.emit_api_metrics=false` выключает remote metric emission для `/api` и `/info`;
- при этом in-process traces, `Server-Timing` и `/info` bottleneck diagnostics остаются доступны.

## Временная backward compatibility

Пока ещё поддерживаются два старых compatibility хвоста:

- `runtime.dev_mode_metrics=true` трактуется как `stages`;
- `METRICS_DELIVERY_MODE` может временно переопределять YAML для operator disable/restore.

Это compatibility detail, а не желаемый долгосрочный способ настройки.

## Секреты

Секреты не живут в repo config files:

- Google credentials
- Object Storage credentials
- Telegram token
- LLM provider tokens
- Yandex Cloud service secrets
- `YANDEX_PROMETHEUS_API_KEY`
- `GRAFANA_TOKEN`
- `BROWSER_AUTH_PROXY_SECRET`

Они подаются через env/secret storage и читаются только в loader/bootstrap.

## Browser auth secret wiring

- backend bootstrap читает `BROWSER_AUTH_PROXY_SECRET`;
- backend trust logic использует его в `src/entrypoints/http/access_context.py`;
- test deploy wiring живёт в `.github/workflows/deploy_yc_function_main.yml`;
- prod deploy wiring живёт в `.github/workflows/release_yc_function_prod.yml`;
- внешний auth contour должен использовать тот же Lockbox-backed secret value.

Operator verification steps:
- [../operations/browser-auth.md](../operations/browser-auth.md)

## Google credentials

Локально и в tooling поддерживаются:
- `GOOGLE_KEY_JSON_PATH`
- `GOOGLE_KEY_JSON`
- `GOOGLE_KEY_JSON_B64`

Deploy workflows уже получают `GOOGLE_KEY_JSON` из Lockbox.  
Checked-in `key/` fallback больше не используется.

## Object Storage

Object Storage используется для:
- raw snapshot;
- prep snapshot;
- people snapshot;
- extra metadata;
- attachment binaries;
- job status/history.

## Queue

Queue config задаёт:
- enabled flag;
- queue URLs для `test` и `prod`;
- status/history prefixes;
- endpoint/auth data для live queue introspection.

## Deploy workflows

- `.github/workflows/deploy_yc_function_main.yml` — deploy при push в `test`
- `.github/workflows/release_yc_function_prod.yml` — ручной prod release

## Config policy

- `os.getenv()` не должен использоваться вне loader/bootstrap;
- сервисы получают typed config objects;
- env-driven branching должен жить в bootstrap/policy selection, а не в core services.

## People registry

- `config/tables.yaml -> field_maps.people` — source-of-truth mapping для people-registry;
- secret-only route `GET /api/v2/people` использует `BROWSER_AUTH_PROXY_SECRET`;
- people snapshot хранится отдельно от frontend payload;
- canonical mail fields:
  - `contact_email` / `contactEmail`
  - `yandex_email` / `yandexEmail`
- canonical derived activity field:
  - `is_active` / `isActive`

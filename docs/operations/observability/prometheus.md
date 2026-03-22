# Prometheus Integration

## Зачем это нужно

Prometheus-compatible sink нужен как второй metrics backend, чтобы Grafana могла быть основной dashboard поверхностью, не ломая уже существующую observability через Yandex Monitoring.

## Текущая политика

Используется dual write:

- `YandexMonitoringMetricsClient` остаётся;
- `YandexManagedPrometheusRemoteWriteClient` добавляется как второй sink;
- при включении обоих используется `CompositeMetricsClient`.

Это даёт Grafana без перестройки instrumentation points.

## Что при этом не меняется

- topology runtime остаётся прежней;
- одна Cloud Function на контур принимает и HTTP, и MQ trigger;
- `/info` остаётся операторской control surface.

Prometheus здесь только дополнительный metrics sink.

## Конфиг

Основной конфиг живёт в:

- `config/runtime.yaml`
- `src/config/schema.py`
- `src/config/loader.py`

Секция `prometheus` задаёт:
- включение;
- backend;
- write endpoint;
- folder/workspace ids;
- service/namespace labels;
- timeout.

## Поведение backend

`YandexManagedPrometheusRemoteWriteClient`:

- использует тот же `MetricsClient` interface;
- нормализует metric names в Prometheus-safe форму;
- пишет через Remote Write;
- сохраняет `env`, `module`, `operation`, `result`;
- добавляет глобальные labels `service="dtm"` и `namespace="dtm"`;
- не валит бизнес-операции при ошибке write path.

## Секреты

Основной секрет:
- `YANDEX_PROMETHEUS_API_KEY`

Совместимый fallback name пока ещё поддерживается:
- `YMP_API_KEY`

Секрет читается только в `src/platform/bootstrap.py`.

## Текущее состояние

Repo-side foundation уже собран:

- typed config;
- remote-write backend;
- composite dual-write client;
- additive `/info` metadata;
- Grafana dashboard spec.

## Путь к валидации

1. deploy `test` с `prometheus.enabled=true`;
2. убедиться, что sample ingestion живой;
3. открыть Grafana dashboard и проверить непустые panels.

## Failure policy

Prometheus emission остаётся best-effort:

- ошибки логируются;
- Monitoring sink остаётся рабочим;
- `/info` продолжает быть usable независимо от Prometheus.

# Grafana Dashboard

## Зачем он нужен

Grafana — это основная human-facing dashboard поверхность для операторов.  
При этом базовая observability через Monitoring и `/info` остаётся на месте.

## Выбранная схема

- Grafana работает на VPS владельца;
- datasource — Prometheus-compatible backend;
- основной target — Yandex Managed Service for Prometheus;
- для встраивания во внешнюю страницу используется iframe/public dashboard path.

## Роль репозитория

Репозиторий хранит:

- typed config для Grafana;
- dashboard specification в `src/platform/integrations/grafana/specs.py`;
- optional API helpers в `src/platform/integrations/grafana/api.py`;
- export script `scripts/render_grafana_dashboard.py`.

Именно repo остаётся source of truth для:
- структуры панелей;
- query intent;
- dashboard UID и canonical URLs.

## Что показывает dashboard

- snapshot, render, API, worker, notify и telegram activity;
- bottleneck panels для frontend/read paths;
- outer-vs-inner latency breakdown для `/api`;
- wall-clock и metrics flush diagnostics;
- отдельные stat panels для render operations.

Это operator dashboard, а не BI-витрина.

## Правила layout

- stat cards компактные, чтобы на одном экране помещалось больше текущей диагностики;
- timeseries panels по возможности занимают половину ширины;
- render panels разделены по операциям, а не слиты в один усреднённый график.

## `/info` и Grafana

`/info` не заменяется Grafana.

`/info` остаётся:
- control surface;
- summary view;
- точкой входа для live diagnostics и attachment harness.

Grafana нужен как обзорная dashboard поверхность поверх метрик.

## Текущее состояние

Repo-side foundation уже собран:

- dashboard spec в коде есть;
- folder creation и dashboard import работают;
- public dashboard URL и embed URL заведены;
- layout публикуется из repo spec, а не редактируется вручную в Grafana.

## Практические caveats

- iframe embed всё ещё зависит от server-side `allow_embedding = true`;
- public dashboard не заменяет прямые Monitoring/Prometheus queries;
- финальная настройка workspace и datasource описана в [yandex-prometheus-workspace-setup.md](yandex-prometheus-workspace-setup.md).

## Экспорт из репозитория

```powershell
python scripts/render_grafana_dashboard.py --env test --output work/tmp/dtm_test_ops_dashboard.json
```

## Datasource provisioning

```powershell
python scripts/provision_grafana_datasource.py --env test --workspace-id <workspace_id>
```

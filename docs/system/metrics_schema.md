# Metrics Schema

## Required labels

- `env`
- `module`
- `operation`
- `result`

## Naming rules

- counters: `*_total`
- timings: `*_duration_ms` or specific `*_ms`
- gauges: `*_current`, `*_seconds`, or domain-specific current value names

## Groups

### Snapshot

- `dtm.snapshot.update_total`
- `dtm.snapshot.update_duration_ms`
- `dtm.snapshot.fetch_sheet_ms`
- `dtm.snapshot.fetch_sheet_last_ms`
- `dtm.snapshot.fetch_sheet_last5_avg_ms`
- `dtm.snapshot.normalize_ms`
- `dtm.snapshot.normalize_last_ms`
- `dtm.snapshot.normalize_last5_avg_ms`
- `dtm.snapshot.build_prep_ms`
- `dtm.snapshot.build_prep_last_ms`
- `dtm.snapshot.build_prep_last5_avg_ms`
- `dtm.snapshot.extra_load_ms`
- `dtm.snapshot.extra_load_last_ms`
- `dtm.snapshot.extra_load_last5_avg_ms`
- `dtm.snapshot.orphan_reconcile_ms`
- `dtm.snapshot.orphan_reconcile_last_ms`
- `dtm.snapshot.orphan_reconcile_last5_avg_ms`
- `dtm.snapshot.task_view_build_ms`
- `dtm.snapshot.task_view_build_last_ms`
- `dtm.snapshot.task_view_build_last5_avg_ms`
- `dtm.snapshot.prep_index_build_ms`
- `dtm.snapshot.prep_index_build_last_ms`
- `dtm.snapshot.prep_index_build_last5_avg_ms`
- `dtm.snapshot.write_raw_ms`
- `dtm.snapshot.write_raw_last_ms`
- `dtm.snapshot.write_raw_last5_avg_ms`
- `dtm.snapshot.write_prep_ms`
- `dtm.snapshot.write_prep_last_ms`
- `dtm.snapshot.write_prep_last5_avg_ms`
- `dtm.snapshot.changed_total`
- `dtm.snapshot.nochange_total`

### API

- `dtm.api.requests_total`
- `dtm.api.duration_ms`
- `dtm.api.response_size_bytes`
- `dtm.api.prep_age_seconds`

### Render

- `dtm.render.total`
- `dtm.render.duration_ms`
- `dtm.render.duration_last_ms`
- `dtm.render.duration_last5_avg_ms`
- `dtm.render.build_plan_ms`
- `dtm.render.build_plan_last_ms`
- `dtm.render.build_plan_last5_avg_ms`
- `dtm.render.write_sheet_ms`
- `dtm.render.write_sheet_last_ms`
- `dtm.render.write_sheet_last5_avg_ms`
- `dtm.render.rows_rendered`
- `dtm.render.cells_written`

### Notify

- `dtm.notify.total`
- `dtm.notify.duration_ms`
- `dtm.notify.selection_ms`
- `dtm.notify.formatting_ms`
- `dtm.notify.send_ms`
- `dtm.notify.messages_sent`
- `dtm.notify.tasks_selected`

### Telegram

- `dtm.telegram.updates_total`
- `dtm.telegram.accepted_total`
- `dtm.telegram.rejected_total`
- `dtm.telegram.enqueue_ms`
- `dtm.telegram.command_total`

### Worker / Queue

- `dtm.worker.commands_total`
- `dtm.worker.command_duration_ms`
- `dtm.worker.command_failures_total`
- `dtm.worker.command_retries_total`
- `dtm.worker.dlq_total`

## Current implementation notes

`src/observability/*` is the shared abstraction layer for metrics and timing wrappers.

Snapshot runtime notes:

- `fetch_sheet_ms` now covers one values read plus one canonical `A`-column color read only.
- `normalize_ms` no longer includes a second Google color fetch.
- `*_last_ms` and `*_last5_avg_ms` gauges are emitted from recent successful job history, not approximated in Grafana queries.

Current runtime default:

- `NoopMetricsClient`

This keeps instrumentation points stable even before a real Yandex Monitoring adapter is wired in production.

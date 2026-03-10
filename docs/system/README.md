# System docs

## Current runtime docs
- `architecture.md` — current high-level runtime architecture
- `dataflow.md` — canonical snapshot/queue/data flow
- `runtime_modes.md` — supported standard runtime modes
- `entrypoints_index_main.md` — thin entrypoint and runtime shell map
- `module_map.md` — active module map
- `config.md` — current typed config and deploy/config surface
- `contracts.md` — current data contracts
- `runbook.md` — operator/developer runbook
- `queue_retry_policy.md` — current queue-driven retry semantics
- `job_status_schema.md` — current job-status vocabulary and storage shape
- `metrics_schema.md` — observability metric names and required labels
- `yc_monitoring_integration.md` — current Monitoring backend wiring, auth model, and rollout policy
- `prometheus_integration.md` — Prometheus-compatible second sink and dual-write policy for Grafana
- `grafana_ops_dashboard.md` — Grafana dashboard structure, metadata, and embed policy
- `grafana_vps_setup.md` — hands-on VPS setup steps for Grafana, datasource, dashboard import, and iframe enablement
- `yandex_prometheus_workspace_setup.md` — exact manual YMP workspace/API-key steps and the repo command that provisions the Grafana datasource
- `datalens_ops_dashboard.md` — DataLens operator dashboard structure and provisioning notes
- `command_runtime_architecture.md` — current HTTP/intake/worker runtime flow
- `yandex_queue_setup.md` — current queue/DLQ/trigger topology
- `telegram_webhook_setup.md` — current webhook hardening/setup rules
- `telegram_commands.md` — current internal Telegram command taxonomy
- `telegram_command_matrix.md` — current Telegram user-action to internal-command map

## Future skeleton references
- `command_queue_skeleton.md`
- `telegram_intake_skeleton.md`
- `file_attachments_skeleton.md`
- `group_query_unification_skeleton.md`

## Archive policy
- stale migration/checklist/investigation docs live in `docs/archive/system_legacy/`
- `docs/system/` must describe only the current runtime or currently accepted future skeletons

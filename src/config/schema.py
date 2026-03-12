"""Typed configuration schema for YAML-based runtime settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeSection:
    env_default: str = "dev"
    strict_env_guard_default: bool = False
    timezone: str = "Europe/Moscow"
    dev_mode_metrics: bool = False
    bottleneck_metrics_level: str = "off"


@dataclass(slots=True)
class MonitoringSection:
    enabled: bool = False
    backend: str = "yandex_monitoring"
    folder_id: str = ""
    endpoint_write: str = "https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write"
    service: str = "custom"
    namespace: str = "dtm"
    dashboard_name_test: str = "DTM Test Observability"
    dashboard_name_prod: str = "DTM Prod Observability"
    dashboard_id_test: str = ""
    dashboard_id_prod: str = ""
    emit_queue_metrics: bool = True
    emit_api_metrics: bool = True
    emit_snapshot_metrics: bool = True
    emit_render_metrics: bool = True
    emit_notify_metrics: bool = True
    emit_telegram_metrics: bool = True


@dataclass(slots=True)
class DataLensSection:
    enabled: bool = False
    org_id: str = ""
    workbook_name: str = "DTM Observability"
    workbook_id_test: str = ""
    workbook_id_prod: str = ""
    connection_name_test: str = "DTM Monitoring Test"
    connection_name_prod: str = "DTM Monitoring Prod"
    connection_id_test: str = ""
    connection_id_prod: str = ""
    dashboard_name_test: str = "DTM Test Ops"
    dashboard_name_prod: str = "DTM Prod Ops"
    dashboard_id_test: str = ""
    dashboard_id_prod: str = ""
    dashboard_url_test: str = ""
    dashboard_url_prod: str = ""


@dataclass(slots=True)
class PrometheusSection:
    enabled: bool = False
    backend: str = "yandex_managed_prometheus"
    endpoint_write: str = ""
    folder_id: str = ""
    workspace_id_test: str = ""
    workspace_id_prod: str = ""
    service: str = "dtm"
    namespace: str = "dtm"
    timeout_seconds: float = 2.0


@dataclass(slots=True)
class GrafanaSection:
    enabled: bool = False
    public_base_url: str = ""
    dashboard_uid_test: str = ""
    dashboard_uid_prod: str = ""
    dashboard_url_test: str = ""
    dashboard_url_prod: str = ""
    embed_url_test: str = ""
    embed_url_prod: str = ""
    folder_name_test: str = "DTM Test"
    folder_name_prod: str = "DTM Prod"


@dataclass(slots=True)
class PipelineSection:
    readmodel_ttl_minutes: int = 9
    preflight_top_rows: int = 50
    full_sync_interval_hours: int = 24
    force_refresh_default: bool = False


@dataclass(slots=True)
class SnapshotEngineSection:
    enabled: bool = False
    storage: str = "s3"
    bucket: str = ""
    prefix_raw: str = "snapshots/raw/default.json"
    prefix_prep: str = "snapshots/prep/default.json"
    prefix_extra: str = "snapshots/extra/"
    prefix_people: str = "snapshots/people/default.json"
    prefix_responses: str = "snapshots/responses/"
    force_refresh_default: bool = False


@dataclass(slots=True)
class QueueSection:
    enabled: bool = False
    provider: str = "yandex_message_queue"
    endpoint_url: str = "https://message-queue.api.cloud.yandex.net"
    test_queue_url: str = ""
    prod_queue_url: str = ""
    status_prefix: str = "jobs/{env}/status/"
    latest_prefix: str = "jobs/{env}/latest/"


@dataclass(slots=True)
class TelegramSection:
    webhook_path: str = "/telegram"
    allowed_updates: list[str] = field(default_factory=lambda: ["message", "callback_query"])
    max_connections: int = 5
    secret_required: bool = True


@dataclass(slots=True)
class NotifySection:
    enhance_concurrency: int = 4
    send_retry_attempts: int = 3
    send_retry_backoff_seconds: float = 0.5
    send_retry_backoff_multiplier: float = 2.0
    test_chat_id_override: str = ""
    llm_mode_default: str = "provider"


@dataclass(slots=True)
class SourcesSection:
    store_mode_default: str = "legacy"
    readmodel_source_default: str = "legacy"
    notify_source_default: str = "readmodel_source"
    render_source_default: str = "readmodel_source"


@dataclass(slots=True)
class TimingSection:
    year_mode_default: str = "legacy"
    allowed_year_modes: list[str] = field(default_factory=lambda: ["legacy", "anchors", "chain"])


@dataclass(slots=True)
class RuntimeConfig:
    runtime: RuntimeSection = field(default_factory=RuntimeSection)
    monitoring: MonitoringSection = field(default_factory=MonitoringSection)
    datalens: DataLensSection = field(default_factory=DataLensSection)
    prometheus: PrometheusSection = field(default_factory=PrometheusSection)
    grafana: GrafanaSection = field(default_factory=GrafanaSection)
    web: dict[str, Any] = field(default_factory=dict)
    api: dict[str, Any] = field(default_factory=dict)
    pipeline: PipelineSection = field(default_factory=PipelineSection)
    snapshot_engine: SnapshotEngineSection = field(default_factory=SnapshotEngineSection)
    queue: QueueSection = field(default_factory=QueueSection)
    telegram: TelegramSection = field(default_factory=TelegramSection)
    notify: NotifySection = field(default_factory=NotifySection)
    sources: SourcesSection = field(default_factory=SourcesSection)
    timing: TimingSection = field(default_factory=TimingSection)
    triggers: dict[str, str] = field(default_factory=dict)
    migration: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TablesConfig:
    google_sheets: dict[str, Any] = field(default_factory=dict)
    sheet_names: dict[str, str] = field(default_factory=dict)
    field_maps: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass(slots=True)
class DbConfig:
    ydb: dict[str, Any] = field(default_factory=dict)
    object_storage: dict[str, Any] = field(default_factory=dict)
    tables: dict[str, str] = field(default_factory=dict)
    readmodel: dict[str, Any] = field(default_factory=dict)
    compat: dict[str, Any] = field(default_factory=dict)
    retry: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LlmConfig:
    llm: dict[str, Any] = field(default_factory=dict)
    models: dict[str, Any] = field(default_factory=dict)
    http: dict[str, Any] = field(default_factory=dict)
    failover: dict[str, Any] = field(default_factory=dict)
    assistant: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MappingConfig:
    status_by_color: dict[str, str] = field(default_factory=dict)
    palette: dict[str, str] = field(default_factory=dict)
    project_aliases: dict[str, str] = field(default_factory=dict)
    hidden_stage_names: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DeployCloudConfig:
    folder_id: str = ""
    service_account_id: str = ""
    function_entrypoint: str = "index.handler"
    function_runtime: str = "python311"
    function_timeout: str = "240s"
    function_memory: str = "512Mb"
    function_name_test: str = ""
    function_name_prod: str = ""


@dataclass(slots=True)
class DeployConfig:
    yandex_cloud: DeployCloudConfig = field(default_factory=DeployCloudConfig)


@dataclass(slots=True)
class AppConfig:
    runtime: RuntimeConfig
    tables: TablesConfig
    db: DbConfig
    llm: LlmConfig
    mapping: MappingConfig
    deploy: DeployConfig

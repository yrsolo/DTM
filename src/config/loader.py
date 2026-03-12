"""YAML configuration loader with minimal ENV allowlist overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.config.schema import (
    AppConfig,
    DbConfig,
    DeployConfig,
    LlmConfig,
    MappingConfig,
    RuntimeConfig,
    TablesConfig,
)

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML dependency is required for config loader.") from exc


CONFIG_DIR = Path("config")

# ENV keys that are allowed to override YAML defaults.
ENV_ALLOWLIST = frozenset(
    {
        "ENV",
        "STRICT_ENV_GUARD",
        "DEV_MODE_METRICS",
        "STORE_MODE",
        "READMODEL_SOURCE",
        "NOTIFY_SOURCE",
        "RENDER_SOURCE",
        "TIMING_YEAR_MODE",
        "READMODEL_TTL_MINUTES",
        "PREFLIGHT_TOP_ROWS",
        "FULL_SYNC_INTERVAL_HOURS",
        "FORCE_REFRESH",
        "LEGACY_BLOB_WRITE",
        "WRITE_LEGACY_MILESTONES",
        "SOURCE_SHEET_NAME",
        "TARGET_SHEET_NAME",
        "WEB_DOMAIN",
        "API_DOMAIN_TEST",
        "API_DOMAIN_PROD",
        "DEBUG_HTTP_EVENT",
        "LLM_PROVIDER",
        "OPENAI_MODEL",
        "GOOGLE_LLM_MODEL",
        "YANDEX_LLM_MODEL_URI",
        "LLM_HTTP_TIMEOUT_SECONDS",
        "LLM_HTTP_RETRY_ATTEMPTS",
        "LLM_HTTP_RETRY_BACKOFF_SECONDS",
        "LLM_FAILOVER_MODE",
        "LLM_FAILOVER_PROVIDER",
        "TG_BOT_USERNAME",
        "DEFAULT_CHAT_ID",
        "PROXY_URL",
        "MONITORING_ENABLED",
        "MONITORING_BACKEND",
        "MONITORING_FOLDER_ID",
        "MONITORING_SERVICE",
        "MONITORING_NAMESPACE",
        "MONITORING_DASHBOARD_NAME",
        "DATALENS_ENABLED",
        "DATALENS_ORG_ID",
        "PROMETHEUS_ENABLED",
        "PROMETHEUS_BACKEND",
        "PROMETHEUS_ENDPOINT_WRITE",
        "PROMETHEUS_FOLDER_ID",
        "GRAFANA_ENABLED",
        "GRAFANA_PUBLIC_BASE_URL",
    }
)

# Secrets/deployment-specific keys intentionally stay only in ENV.
ENV_SECRETS_ONLY = frozenset(
    {
        "YC_SA_JSON_CREDENTIALS",
        "YC_SA_KEY_FILE",
        "GOOGLE_KEY_JSON_PATH",
        "GOOGLE_KEY_JSON_B64",
        "GOOGLE_KEY_JSON",
        "TG_TOKEN",
        "OPENAI_TOKEN",
        "ORG_TOKEN",
        "GOOGLE_LLM_API_KEY",
        "YANDEX_LLM_API_KEY",
        "PUBLIC_BASE_URL",
    }
)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file) or {}
    if not isinstance(content, dict):
        raise ValueError(f"Config file must contain top-level object: {path}")
    return content


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _merge_runtime_env_overrides(runtime_cfg: RuntimeConfig) -> RuntimeConfig:
    env_mode = os.getenv("ENV", runtime_cfg.runtime.env_default).strip().lower() or runtime_cfg.runtime.env_default
    runtime_cfg.runtime.env_default = env_mode

    if "STRICT_ENV_GUARD" in os.environ:
        runtime_cfg.runtime.strict_env_guard_default = _parse_bool(os.environ["STRICT_ENV_GUARD"])
    if "DEV_MODE_METRICS" in os.environ:
        runtime_cfg.runtime.dev_mode_metrics = _parse_bool(os.environ["DEV_MODE_METRICS"])

    if "READMODEL_TTL_MINUTES" in os.environ:
        runtime_cfg.pipeline.readmodel_ttl_minutes = max(1, int(os.environ["READMODEL_TTL_MINUTES"]))
    if "PREFLIGHT_TOP_ROWS" in os.environ:
        runtime_cfg.pipeline.preflight_top_rows = max(1, int(os.environ["PREFLIGHT_TOP_ROWS"]))
    if "FULL_SYNC_INTERVAL_HOURS" in os.environ:
        runtime_cfg.pipeline.full_sync_interval_hours = max(1, int(os.environ["FULL_SYNC_INTERVAL_HOURS"]))
    if "FORCE_REFRESH" in os.environ:
        runtime_cfg.pipeline.force_refresh_default = _parse_bool(os.environ["FORCE_REFRESH"])

    if "STORE_MODE" in os.environ:
        runtime_cfg.sources.store_mode_default = os.environ["STORE_MODE"].strip().lower()
    if "READMODEL_SOURCE" in os.environ:
        runtime_cfg.sources.readmodel_source_default = os.environ["READMODEL_SOURCE"].strip().lower()
    if "NOTIFY_SOURCE" in os.environ:
        runtime_cfg.sources.notify_source_default = os.environ["NOTIFY_SOURCE"].strip().lower()
    if "RENDER_SOURCE" in os.environ:
        runtime_cfg.sources.render_source_default = os.environ["RENDER_SOURCE"].strip().lower()

    if "TIMING_YEAR_MODE" in os.environ:
        runtime_cfg.timing.year_mode_default = os.environ["TIMING_YEAR_MODE"].strip().lower()

    if "MONITORING_ENABLED" in os.environ:
        runtime_cfg.monitoring.enabled = _parse_bool(os.environ["MONITORING_ENABLED"])
    if "MONITORING_BACKEND" in os.environ:
        runtime_cfg.monitoring.backend = os.environ["MONITORING_BACKEND"].strip().lower()
    if "MONITORING_FOLDER_ID" in os.environ:
        runtime_cfg.monitoring.folder_id = os.environ["MONITORING_FOLDER_ID"].strip()
    if "MONITORING_SERVICE" in os.environ:
        runtime_cfg.monitoring.service = os.environ["MONITORING_SERVICE"].strip()
    if "MONITORING_NAMESPACE" in os.environ:
        runtime_cfg.monitoring.namespace = os.environ["MONITORING_NAMESPACE"].strip()
    if "MONITORING_DASHBOARD_NAME" in os.environ:
        dashboard_name = os.environ["MONITORING_DASHBOARD_NAME"].strip()
        env_mode = str(runtime_cfg.runtime.env_default or "").strip().lower()
        if env_mode == "prod":
            runtime_cfg.monitoring.dashboard_name_prod = dashboard_name
        else:
            runtime_cfg.monitoring.dashboard_name_test = dashboard_name
    if "DATALENS_ENABLED" in os.environ:
        runtime_cfg.datalens.enabled = _parse_bool(os.environ["DATALENS_ENABLED"])
    if "DATALENS_ORG_ID" in os.environ:
        runtime_cfg.datalens.org_id = os.environ["DATALENS_ORG_ID"].strip()
    if "PROMETHEUS_ENABLED" in os.environ:
        runtime_cfg.prometheus.enabled = _parse_bool(os.environ["PROMETHEUS_ENABLED"])
    if "PROMETHEUS_BACKEND" in os.environ:
        runtime_cfg.prometheus.backend = os.environ["PROMETHEUS_BACKEND"].strip().lower()
    if "PROMETHEUS_ENDPOINT_WRITE" in os.environ:
        runtime_cfg.prometheus.endpoint_write = os.environ["PROMETHEUS_ENDPOINT_WRITE"].strip()
    if "PROMETHEUS_FOLDER_ID" in os.environ:
        runtime_cfg.prometheus.folder_id = os.environ["PROMETHEUS_FOLDER_ID"].strip()
    if "GRAFANA_ENABLED" in os.environ:
        runtime_cfg.grafana.enabled = _parse_bool(os.environ["GRAFANA_ENABLED"])
    if "GRAFANA_PUBLIC_BASE_URL" in os.environ:
        runtime_cfg.grafana.public_base_url = os.environ["GRAFANA_PUBLIC_BASE_URL"].strip()

    return runtime_cfg


def _runtime_from_dict(data: dict[str, Any]) -> RuntimeConfig:
    defaults = RuntimeConfig()
    runtime_raw = data.get("runtime", {}) if isinstance(data.get("runtime", {}), dict) else {}
    web_raw = data.get("web", {}) if isinstance(data.get("web", {}), dict) else {}
    api_raw = data.get("api", {}) if isinstance(data.get("api", {}), dict) else {}
    pipeline_raw = data.get("pipeline", {}) if isinstance(data.get("pipeline", {}), dict) else {}
    snapshot_engine_raw = (
        data.get("snapshot_engine", {})
        if isinstance(data.get("snapshot_engine", {}), dict)
        else {}
    )
    monitoring_raw = data.get("monitoring", {}) if isinstance(data.get("monitoring", {}), dict) else {}
    datalens_raw = data.get("datalens", {}) if isinstance(data.get("datalens", {}), dict) else {}
    prometheus_raw = data.get("prometheus", {}) if isinstance(data.get("prometheus", {}), dict) else {}
    grafana_raw = data.get("grafana", {}) if isinstance(data.get("grafana", {}), dict) else {}
    telegram_raw = data.get("telegram", {}) if isinstance(data.get("telegram", {}), dict) else {}
    notify_raw = data.get("notify", {}) if isinstance(data.get("notify", {}), dict) else {}
    queue_raw = data.get("queue", {}) if isinstance(data.get("queue", {}), dict) else {}
    sources_raw = data.get("sources", {}) if isinstance(data.get("sources", {}), dict) else {}
    timing_raw = data.get("timing", {}) if isinstance(data.get("timing", {}), dict) else {}
    triggers_raw = data.get("triggers", {}) if isinstance(data.get("triggers", {}), dict) else {}
    migration_raw = data.get("migration", {}) if isinstance(data.get("migration", {}), dict) else {}

    defaults.runtime.env_default = str(runtime_raw.get("env_default", defaults.runtime.env_default))
    defaults.runtime.strict_env_guard_default = bool(
        runtime_raw.get("strict_env_guard_default", defaults.runtime.strict_env_guard_default)
    )
    defaults.runtime.timezone = str(runtime_raw.get("timezone", defaults.runtime.timezone))
    defaults.runtime.dev_mode_metrics = bool(
        runtime_raw.get("dev_mode_metrics", defaults.runtime.dev_mode_metrics)
    )
    defaults.monitoring.enabled = bool(monitoring_raw.get("enabled", defaults.monitoring.enabled))
    defaults.monitoring.backend = str(monitoring_raw.get("backend", defaults.monitoring.backend))
    defaults.monitoring.folder_id = str(monitoring_raw.get("folder_id", defaults.monitoring.folder_id))
    defaults.monitoring.endpoint_write = str(
        monitoring_raw.get("endpoint_write", defaults.monitoring.endpoint_write)
    )
    defaults.monitoring.service = str(monitoring_raw.get("service", defaults.monitoring.service))
    defaults.monitoring.namespace = str(monitoring_raw.get("namespace", defaults.monitoring.namespace))
    defaults.monitoring.dashboard_name_test = str(
        monitoring_raw.get("dashboard_name_test", defaults.monitoring.dashboard_name_test)
    )
    defaults.monitoring.dashboard_name_prod = str(
        monitoring_raw.get("dashboard_name_prod", defaults.monitoring.dashboard_name_prod)
    )
    defaults.monitoring.dashboard_id_test = str(
        monitoring_raw.get("dashboard_id_test", defaults.monitoring.dashboard_id_test)
    )
    defaults.monitoring.dashboard_id_prod = str(
        monitoring_raw.get("dashboard_id_prod", defaults.monitoring.dashboard_id_prod)
    )
    defaults.monitoring.emit_queue_metrics = bool(
        monitoring_raw.get("emit_queue_metrics", defaults.monitoring.emit_queue_metrics)
    )
    defaults.monitoring.emit_api_metrics = bool(
        monitoring_raw.get("emit_api_metrics", defaults.monitoring.emit_api_metrics)
    )
    defaults.monitoring.emit_snapshot_metrics = bool(
        monitoring_raw.get("emit_snapshot_metrics", defaults.monitoring.emit_snapshot_metrics)
    )
    defaults.monitoring.emit_render_metrics = bool(
        monitoring_raw.get("emit_render_metrics", defaults.monitoring.emit_render_metrics)
    )
    defaults.monitoring.emit_notify_metrics = bool(
        monitoring_raw.get("emit_notify_metrics", defaults.monitoring.emit_notify_metrics)
    )
    defaults.monitoring.emit_telegram_metrics = bool(
        monitoring_raw.get("emit_telegram_metrics", defaults.monitoring.emit_telegram_metrics)
    )
    defaults.datalens.enabled = bool(datalens_raw.get("enabled", defaults.datalens.enabled))
    defaults.datalens.org_id = str(datalens_raw.get("org_id", defaults.datalens.org_id))
    defaults.datalens.workbook_name = str(
        datalens_raw.get("workbook_name", defaults.datalens.workbook_name)
    )
    defaults.datalens.workbook_id_test = str(
        datalens_raw.get("workbook_id_test", defaults.datalens.workbook_id_test)
    )
    defaults.datalens.workbook_id_prod = str(
        datalens_raw.get("workbook_id_prod", defaults.datalens.workbook_id_prod)
    )
    defaults.datalens.connection_name_test = str(
        datalens_raw.get("connection_name_test", defaults.datalens.connection_name_test)
    )
    defaults.datalens.connection_name_prod = str(
        datalens_raw.get("connection_name_prod", defaults.datalens.connection_name_prod)
    )
    defaults.datalens.connection_id_test = str(
        datalens_raw.get("connection_id_test", defaults.datalens.connection_id_test)
    )
    defaults.datalens.connection_id_prod = str(
        datalens_raw.get("connection_id_prod", defaults.datalens.connection_id_prod)
    )
    defaults.datalens.dashboard_name_test = str(
        datalens_raw.get("dashboard_name_test", defaults.datalens.dashboard_name_test)
    )
    defaults.datalens.dashboard_name_prod = str(
        datalens_raw.get("dashboard_name_prod", defaults.datalens.dashboard_name_prod)
    )
    defaults.datalens.dashboard_id_test = str(
        datalens_raw.get("dashboard_id_test", defaults.datalens.dashboard_id_test)
    )
    defaults.datalens.dashboard_id_prod = str(
        datalens_raw.get("dashboard_id_prod", defaults.datalens.dashboard_id_prod)
    )
    defaults.datalens.dashboard_url_test = str(
        datalens_raw.get("dashboard_url_test", defaults.datalens.dashboard_url_test)
    )
    defaults.datalens.dashboard_url_prod = str(
        datalens_raw.get("dashboard_url_prod", defaults.datalens.dashboard_url_prod)
    )
    defaults.prometheus.enabled = bool(prometheus_raw.get("enabled", defaults.prometheus.enabled))
    defaults.prometheus.backend = str(prometheus_raw.get("backend", defaults.prometheus.backend))
    defaults.prometheus.endpoint_write = str(
        prometheus_raw.get("endpoint_write", defaults.prometheus.endpoint_write)
    )
    defaults.prometheus.folder_id = str(prometheus_raw.get("folder_id", defaults.prometheus.folder_id))
    defaults.prometheus.workspace_id_test = str(
        prometheus_raw.get("workspace_id_test", defaults.prometheus.workspace_id_test)
    )
    defaults.prometheus.workspace_id_prod = str(
        prometheus_raw.get("workspace_id_prod", defaults.prometheus.workspace_id_prod)
    )
    defaults.prometheus.service = str(prometheus_raw.get("service", defaults.prometheus.service))
    defaults.prometheus.namespace = str(
        prometheus_raw.get("namespace", defaults.prometheus.namespace)
    )
    defaults.prometheus.timeout_seconds = float(
        prometheus_raw.get("timeout_seconds", defaults.prometheus.timeout_seconds)
    )
    defaults.grafana.enabled = bool(grafana_raw.get("enabled", defaults.grafana.enabled))
    defaults.grafana.public_base_url = str(
        grafana_raw.get("public_base_url", defaults.grafana.public_base_url)
    )
    defaults.grafana.dashboard_uid_test = str(
        grafana_raw.get("dashboard_uid_test", defaults.grafana.dashboard_uid_test)
    )
    defaults.grafana.dashboard_uid_prod = str(
        grafana_raw.get("dashboard_uid_prod", defaults.grafana.dashboard_uid_prod)
    )
    defaults.grafana.dashboard_url_test = str(
        grafana_raw.get("dashboard_url_test", defaults.grafana.dashboard_url_test)
    )
    defaults.grafana.dashboard_url_prod = str(
        grafana_raw.get("dashboard_url_prod", defaults.grafana.dashboard_url_prod)
    )
    defaults.grafana.embed_url_test = str(
        grafana_raw.get("embed_url_test", defaults.grafana.embed_url_test)
    )
    defaults.grafana.embed_url_prod = str(
        grafana_raw.get("embed_url_prod", defaults.grafana.embed_url_prod)
    )
    defaults.grafana.folder_name_test = str(
        grafana_raw.get("folder_name_test", defaults.grafana.folder_name_test)
    )
    defaults.grafana.folder_name_prod = str(
        grafana_raw.get("folder_name_prod", defaults.grafana.folder_name_prod)
    )
    defaults.web = {str(k): v for k, v in web_raw.items()}
    defaults.api = {str(k): v for k, v in api_raw.items()}

    defaults.pipeline.readmodel_ttl_minutes = int(
        pipeline_raw.get("readmodel_ttl_minutes", defaults.pipeline.readmodel_ttl_minutes)
    )
    defaults.pipeline.preflight_top_rows = int(
        pipeline_raw.get("preflight_top_rows", defaults.pipeline.preflight_top_rows)
    )
    defaults.pipeline.full_sync_interval_hours = int(
        pipeline_raw.get("full_sync_interval_hours", defaults.pipeline.full_sync_interval_hours)
    )
    defaults.pipeline.force_refresh_default = bool(
        pipeline_raw.get("force_refresh_default", defaults.pipeline.force_refresh_default)
    )
    defaults.snapshot_engine.enabled = bool(
        snapshot_engine_raw.get("enabled", defaults.snapshot_engine.enabled)
    )
    defaults.snapshot_engine.storage = str(
        snapshot_engine_raw.get("storage", defaults.snapshot_engine.storage)
    )
    defaults.snapshot_engine.bucket = str(
        snapshot_engine_raw.get("bucket", defaults.snapshot_engine.bucket)
    )
    defaults.snapshot_engine.prefix_raw = str(
        snapshot_engine_raw.get("prefix_raw", defaults.snapshot_engine.prefix_raw)
    )
    defaults.snapshot_engine.prefix_prep = str(
        snapshot_engine_raw.get("prefix_prep", defaults.snapshot_engine.prefix_prep)
    )
    defaults.snapshot_engine.prefix_extra = str(
        snapshot_engine_raw.get("prefix_extra", defaults.snapshot_engine.prefix_extra)
    )
    defaults.snapshot_engine.prefix_people = str(
        snapshot_engine_raw.get("prefix_people", defaults.snapshot_engine.prefix_people)
    )
    defaults.snapshot_engine.prefix_responses = str(
        snapshot_engine_raw.get("prefix_responses", defaults.snapshot_engine.prefix_responses)
    )
    defaults.snapshot_engine.force_refresh_default = bool(
        snapshot_engine_raw.get("force_refresh_default", defaults.snapshot_engine.force_refresh_default)
    )
    defaults.queue.enabled = bool(queue_raw.get("enabled", defaults.queue.enabled))
    defaults.queue.provider = str(queue_raw.get("provider", defaults.queue.provider))
    defaults.queue.endpoint_url = str(queue_raw.get("endpoint_url", defaults.queue.endpoint_url))
    defaults.queue.test_queue_url = str(queue_raw.get("test_queue_url", defaults.queue.test_queue_url))
    defaults.queue.prod_queue_url = str(queue_raw.get("prod_queue_url", defaults.queue.prod_queue_url))
    defaults.queue.status_prefix = str(queue_raw.get("status_prefix", defaults.queue.status_prefix))
    defaults.queue.latest_prefix = str(queue_raw.get("latest_prefix", defaults.queue.latest_prefix))
    defaults.telegram.webhook_path = str(telegram_raw.get("webhook_path", defaults.telegram.webhook_path))
    allowed_updates = telegram_raw.get("allowed_updates", defaults.telegram.allowed_updates)
    if isinstance(allowed_updates, list):
        defaults.telegram.allowed_updates = [str(item).strip() for item in allowed_updates if str(item).strip()]
    defaults.telegram.max_connections = int(telegram_raw.get("max_connections", defaults.telegram.max_connections))
    defaults.telegram.secret_required = bool(telegram_raw.get("secret_required", defaults.telegram.secret_required))
    defaults.notify.enhance_concurrency = int(
        notify_raw.get("enhance_concurrency", defaults.notify.enhance_concurrency)
    )
    defaults.notify.send_retry_attempts = int(
        notify_raw.get("send_retry_attempts", defaults.notify.send_retry_attempts)
    )
    defaults.notify.send_retry_backoff_seconds = float(
        notify_raw.get("send_retry_backoff_seconds", defaults.notify.send_retry_backoff_seconds)
    )
    defaults.notify.send_retry_backoff_multiplier = float(
        notify_raw.get("send_retry_backoff_multiplier", defaults.notify.send_retry_backoff_multiplier)
    )
    defaults.notify.test_chat_id_override = str(
        notify_raw.get("test_chat_id_override", defaults.notify.test_chat_id_override)
    )
    defaults.notify.llm_mode_default = str(
        notify_raw.get("llm_mode_default", defaults.notify.llm_mode_default)
    )

    defaults.sources.store_mode_default = str(
        sources_raw.get("store_mode_default", defaults.sources.store_mode_default)
    )
    defaults.sources.readmodel_source_default = str(
        sources_raw.get("readmodel_source_default", defaults.sources.readmodel_source_default)
    )
    defaults.sources.notify_source_default = str(
        sources_raw.get("notify_source_default", defaults.sources.notify_source_default)
    )
    defaults.sources.render_source_default = str(
        sources_raw.get("render_source_default", defaults.sources.render_source_default)
    )

    defaults.timing.year_mode_default = str(
        timing_raw.get("year_mode_default", defaults.timing.year_mode_default)
    )
    allowed = timing_raw.get("allowed_year_modes", defaults.timing.allowed_year_modes)
    if isinstance(allowed, list):
        defaults.timing.allowed_year_modes = [str(item) for item in allowed]

    defaults.triggers = {str(k): str(v) for k, v in triggers_raw.items()}
    defaults.migration = migration_raw
    return defaults


def _merge_tables_env_overrides(tables_cfg: TablesConfig) -> TablesConfig:
    google_sheets = dict(tables_cfg.google_sheets)
    source_sheet_name = os.getenv("SOURCE_SHEET_NAME", "").strip()
    target_sheet_name = os.getenv("TARGET_SHEET_NAME", "").strip()
    if source_sheet_name:
        google_sheets["source_sheet_name_default"] = source_sheet_name
    if target_sheet_name:
        google_sheets["target_sheet_name_default"] = target_sheet_name
    tables_cfg.google_sheets = google_sheets
    return tables_cfg


def load_config(config_dir: Path = CONFIG_DIR) -> AppConfig:
    runtime_data = _load_yaml(config_dir / "runtime.yaml")
    tables_data = _load_yaml(config_dir / "tables.yaml")
    db_data = _load_yaml(config_dir / "db.yaml")
    llm_data = _load_yaml(config_dir / "llm.yaml")
    mapping_data = _load_yaml(config_dir / "mapping.yaml")
    deploy_data = _load_yaml(config_dir / "deploy.yaml")

    runtime_cfg = _runtime_from_dict(runtime_data)
    runtime_cfg = _merge_runtime_env_overrides(runtime_cfg)
    snapshot_cfg = runtime_cfg.snapshot_engine
    if bool(snapshot_cfg.enabled):
        if str(snapshot_cfg.storage).strip().lower() != "s3":
            raise ValueError("snapshot_engine.storage must be 's3' when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.bucket).strip():
            raise ValueError("snapshot_engine.bucket is required when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.prefix_raw).strip():
            raise ValueError("snapshot_engine.prefix_raw is required when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.prefix_prep).strip():
            raise ValueError("snapshot_engine.prefix_prep is required when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.prefix_extra).strip():
            raise ValueError("snapshot_engine.prefix_extra is required when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.prefix_people).strip():
            raise ValueError("snapshot_engine.prefix_people is required when snapshot_engine.enabled=true")
        if not str(snapshot_cfg.prefix_responses).strip():
            raise ValueError("snapshot_engine.prefix_responses is required when snapshot_engine.enabled=true")
    queue_cfg = runtime_cfg.queue
    if bool(queue_cfg.enabled):
        if str(queue_cfg.provider).strip().lower() != "yandex_message_queue":
            raise ValueError("queue.provider must be 'yandex_message_queue' when queue.enabled=true")
        queue_url = (
            str(queue_cfg.prod_queue_url).strip()
            if str(runtime_cfg.runtime.env_default).strip().lower() == "prod"
            else str(queue_cfg.test_queue_url).strip()
        )
        if not queue_url:
            raise ValueError("Queue URL is required for current env when queue.enabled=true")
        if not str(queue_cfg.status_prefix).strip():
            raise ValueError("queue.status_prefix is required when queue.enabled=true")
        if not str(queue_cfg.latest_prefix).strip():
            raise ValueError("queue.latest_prefix is required when queue.enabled=true")
    monitoring_cfg = runtime_cfg.monitoring
    if bool(monitoring_cfg.enabled):
        if str(monitoring_cfg.backend).strip().lower() != "yandex_monitoring":
            raise ValueError("monitoring.backend must be 'yandex_monitoring' when monitoring.enabled=true")
        folder_id = str(monitoring_cfg.folder_id).strip() or str(
            deploy_data.get("yandex_cloud", {}).get("folder_id", "")
        ).strip()
        if not folder_id:
            raise ValueError(
                "monitoring.folder_id or deploy.yandex_cloud.folder_id is required when monitoring.enabled=true"
            )
        if not str(monitoring_cfg.endpoint_write).strip():
            raise ValueError("monitoring.endpoint_write is required when monitoring.enabled=true")
        if str(monitoring_cfg.service).strip().lower() != "custom":
            raise ValueError("monitoring.service must be 'custom' for Yandex custom metrics")
    datalens_cfg = runtime_cfg.datalens
    if bool(datalens_cfg.enabled):
        if not str(datalens_cfg.org_id).strip():
            raise ValueError("datalens.org_id is required when datalens.enabled=true")
        if not str(datalens_cfg.workbook_name).strip():
            raise ValueError("datalens.workbook_name is required when datalens.enabled=true")
        if not str(datalens_cfg.connection_name_test).strip():
            raise ValueError("datalens.connection_name_test is required when datalens.enabled=true")
        if not str(datalens_cfg.connection_name_prod).strip():
            raise ValueError("datalens.connection_name_prod is required when datalens.enabled=true")
        if not str(datalens_cfg.dashboard_name_test).strip():
            raise ValueError("datalens.dashboard_name_test is required when datalens.enabled=true")
        if not str(datalens_cfg.dashboard_name_prod).strip():
            raise ValueError("datalens.dashboard_name_prod is required when datalens.enabled=true")
    prometheus_cfg = runtime_cfg.prometheus
    if bool(prometheus_cfg.enabled):
        if not str(prometheus_cfg.backend).strip():
            raise ValueError("prometheus.backend is required when prometheus.enabled=true")
        if not str(prometheus_cfg.endpoint_write).strip():
            raise ValueError("prometheus.endpoint_write is required when prometheus.enabled=true")
        if not str(prometheus_cfg.service).strip():
            raise ValueError("prometheus.service is required when prometheus.enabled=true")
        if not str(prometheus_cfg.namespace).strip():
            raise ValueError("prometheus.namespace is required when prometheus.enabled=true")
    grafana_cfg = runtime_cfg.grafana
    if bool(grafana_cfg.enabled):
        if not str(grafana_cfg.public_base_url).strip():
            raise ValueError("grafana.public_base_url is required when grafana.enabled=true")
        if not str(grafana_cfg.folder_name_test).strip():
            raise ValueError("grafana.folder_name_test is required when grafana.enabled=true")
        if not str(grafana_cfg.folder_name_prod).strip():
            raise ValueError("grafana.folder_name_prod is required when grafana.enabled=true")

    tables_cfg = TablesConfig(
        google_sheets=tables_data.get("google_sheets", {}),
        sheet_names=tables_data.get("sheet_names", {}),
        field_maps=tables_data.get("field_maps", {}),
    )
    tables_cfg = _merge_tables_env_overrides(tables_cfg)
    env_name = str(runtime_cfg.runtime.env_default or "").strip().lower()
    source_sheet_name = str(tables_cfg.google_sheets.get("source_sheet_name_default", "")).strip()
    target_sheet_name = str(tables_cfg.google_sheets.get("target_sheet_name_default", "")).strip()
    target_sheet_name_prod = str(tables_cfg.google_sheets.get("target_sheet_name_prod_default", "")).strip()
    if env_name == "prod":
        effective_target = target_sheet_name_prod or target_sheet_name
        if source_sheet_name and effective_target and source_sheet_name == effective_target:
            raise ValueError(
                "Unsafe render contour: source_sheet_name_default equals "
                "target_sheet_name_prod_default in prod. Use a separate target spreadsheet."
            )
    db_cfg = DbConfig(
        ydb=db_data.get("ydb", {}),
        object_storage=db_data.get("object_storage", {}),
        tables=db_data.get("tables", {}),
        readmodel=db_data.get("readmodel", {}),
        compat=db_data.get("compat", {}),
        retry=db_data.get("retry", {}),
    )
    llm_cfg = LlmConfig(
        llm=llm_data.get("llm", {}),
        models=llm_data.get("models", {}),
        http=llm_data.get("http", {}),
        failover=llm_data.get("failover", {}),
        assistant=llm_data.get("assistant", {}),
    )
    mapping_cfg = MappingConfig(
        status_by_color=mapping_data.get("status_by_color", {}),
        palette=mapping_data.get("palette", {}),
        project_aliases=mapping_data.get("project_aliases", {}),
        hidden_stage_names=mapping_data.get("hidden_stage_names", []),
    )
    deploy_cloud_raw = (
        deploy_data.get("yandex_cloud", {})
        if isinstance(deploy_data.get("yandex_cloud", {}), dict)
        else {}
    )
    deploy_cfg = DeployConfig()
    deploy_cfg.yandex_cloud.folder_id = str(
        deploy_cloud_raw.get("folder_id", deploy_cfg.yandex_cloud.folder_id)
    )
    deploy_cfg.yandex_cloud.service_account_id = str(
        deploy_cloud_raw.get("service_account_id", deploy_cfg.yandex_cloud.service_account_id)
    )
    deploy_cfg.yandex_cloud.function_entrypoint = str(
        deploy_cloud_raw.get("function_entrypoint", deploy_cfg.yandex_cloud.function_entrypoint)
    )
    deploy_cfg.yandex_cloud.function_runtime = str(
        deploy_cloud_raw.get("function_runtime", deploy_cfg.yandex_cloud.function_runtime)
    )
    deploy_cfg.yandex_cloud.function_timeout = str(
        deploy_cloud_raw.get("function_timeout", deploy_cfg.yandex_cloud.function_timeout)
    )
    deploy_cfg.yandex_cloud.function_memory = str(
        deploy_cloud_raw.get("function_memory", deploy_cfg.yandex_cloud.function_memory)
    )
    deploy_cfg.yandex_cloud.function_name_test = str(
        deploy_cloud_raw.get("function_name_test", deploy_cfg.yandex_cloud.function_name_test)
    )
    deploy_cfg.yandex_cloud.function_name_prod = str(
        deploy_cloud_raw.get("function_name_prod", deploy_cfg.yandex_cloud.function_name_prod)
    )
    return AppConfig(
        runtime=runtime_cfg,
        tables=tables_cfg,
        db=db_cfg,
        llm=llm_cfg,
        mapping=mapping_cfg,
        deploy=deploy_cfg,
    )


def validate_env_usage() -> list[str]:
    """Return env keys outside allowlist (excluding secrets-only keys)."""

    violations: list[str] = []
    for key in os.environ:
        if key in ENV_SECRETS_ONLY:
            continue
        if key.startswith(("PYTHON", "VIRTUAL_ENV", "PATH", "COMSPEC", "SYSTEMROOT", "TEMP", "TMP", "USERNAME")):
            continue
        if key not in ENV_ALLOWLIST:
            violations.append(key)
    return sorted(violations)

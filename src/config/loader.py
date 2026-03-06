"""YAML configuration loader with minimal ENV allowlist overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.config.schema import (
    AppConfig,
    DbConfig,
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
        "STORE_MODE",
        "READMODEL_SOURCE",
        "NOTIFY_SOURCE",
        "RENDER_SOURCE",
        "TIMING_YEAR_MODE",
        "READMODEL_TTL_MINUTES",
        "PREFLIGHT_TOP_ROWS",
        "FULL_SYNC_INTERVAL_HOURS",
        "FORCE_REFRESH",
        "YDB_ID",
        "YDB_ENDPOINT",
        "YDB_DATABASE",
        "YDB_MIGRATE_ON_START",
        "LEGACY_BLOB_WRITE",
        "WRITE_LEGACY_MILESTONES",
        "YDB_EXHAUSTED_MAX_ATTEMPTS",
        "YDB_EXHAUSTED_BASE_BACKOFF_SECONDS",
        "YDB_EXHAUSTED_MAX_BACKOFF_SECONDS",
        "YDB_EXHAUSTED_JITTER_RATIO",
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
    sources_raw = data.get("sources", {}) if isinstance(data.get("sources", {}), dict) else {}
    timing_raw = data.get("timing", {}) if isinstance(data.get("timing", {}), dict) else {}
    triggers_raw = data.get("triggers", {}) if isinstance(data.get("triggers", {}), dict) else {}
    migration_raw = data.get("migration", {}) if isinstance(data.get("migration", {}), dict) else {}

    defaults.runtime.env_default = str(runtime_raw.get("env_default", defaults.runtime.env_default))
    defaults.runtime.strict_env_guard_default = bool(
        runtime_raw.get("strict_env_guard_default", defaults.runtime.strict_env_guard_default)
    )
    defaults.runtime.timezone = str(runtime_raw.get("timezone", defaults.runtime.timezone))
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
    defaults.snapshot_engine.force_refresh_default = bool(
        snapshot_engine_raw.get("force_refresh_default", defaults.snapshot_engine.force_refresh_default)
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
    return AppConfig(
        runtime=runtime_cfg,
        tables=tables_cfg,
        db=db_cfg,
        llm=llm_cfg,
        mapping=mapping_cfg,
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

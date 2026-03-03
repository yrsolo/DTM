"""Typed configuration schema for YAML-based runtime settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeSection:
    env_default: str = "dev"
    strict_env_guard_default: bool = False
    timezone: str = "Europe/Moscow"


@dataclass(slots=True)
class PipelineSection:
    readmodel_ttl_minutes: int = 9
    preflight_top_rows: int = 50
    full_sync_interval_hours: int = 24
    force_refresh_default: bool = False


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
    web: dict[str, Any] = field(default_factory=dict)
    pipeline: PipelineSection = field(default_factory=PipelineSection)
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
class AppConfig:
    runtime: RuntimeConfig
    tables: TablesConfig
    db: DbConfig
    llm: LlmConfig
    mapping: MappingConfig

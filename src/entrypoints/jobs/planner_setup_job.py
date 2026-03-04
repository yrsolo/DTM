"""Planner/dependencies setup helper for main job flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.entrypoints.jobs.source_switch_job import SourceSwitchRequest


@dataclass(frozen=True)
class PlannerRuntimeBuildRequest:
    key_json: dict[str, Any]
    sheet_info: Any
    dry_run: bool
    mock_external: bool
    cfg: Any
    mode: str
    render_source: str
    notify_source: str
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    build_planner_dependencies: Callable[..., Any]
    planner_cls: Callable[..., Any]
    apply_task_source_switches: Callable[[SourceSwitchRequest], tuple[bool, bool]]
    log: Callable[[str], None]


def build_planner_runtime(request: PlannerRuntimeBuildRequest) -> tuple[Any, Any]:
    dependencies = request.build_planner_dependencies(
        request.key_json,
        request.sheet_info,
        dry_run=request.dry_run,
        mock_external=request.mock_external,
        cfg=request.cfg,
    )
    source_task_repository = dependencies.task_repository
    planner = request.planner_cls(
        request.key_json,
        request.sheet_info,
        mode=request.mode,
        dry_run=request.dry_run,
        mock_external=request.mock_external,
        dependencies=dependencies,
    )
    request.apply_task_source_switches(
        SourceSwitchRequest(
            planner=planner,
            mode=request.mode,
            render_source=request.render_source,
            notify_source=request.notify_source,
            ydb_endpoint=request.ydb_endpoint,
            ydb_database=request.ydb_database,
            ydb_sa_json_credentials=request.ydb_sa_json_credentials,
            ydb_sa_key_file=request.ydb_sa_key_file,
            log=request.log,
        )
    )
    return planner, source_task_repository

"""Planner/dependencies setup helper for main job flow."""

from __future__ import annotations

from typing import Any, Callable


def build_planner_runtime(
    *,
    key_json: dict[str, Any],
    sheet_info: Any,
    dry_run: bool,
    mock_external: bool,
    cfg: Any,
    mode: str,
    render_source: str,
    notify_source: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str | None,
    ydb_sa_key_file: str | None,
    build_planner_dependencies: Callable[..., Any],
    planner_cls: Callable[..., Any],
    apply_task_source_switches: Callable[..., tuple[bool, bool]],
    log: Callable[[str], None],
) -> tuple[Any, Any]:
    dependencies = build_planner_dependencies(
        key_json,
        sheet_info,
        dry_run=dry_run,
        mock_external=mock_external,
        cfg=cfg,
    )
    source_task_repository = dependencies.task_repository
    planner = planner_cls(
        key_json,
        sheet_info,
        mode=mode,
        dry_run=dry_run,
        mock_external=mock_external,
        dependencies=dependencies,
    )
    apply_task_source_switches(
        planner=planner,
        mode=mode,
        render_source=render_source,
        notify_source=notify_source,
        ydb_endpoint=ydb_endpoint,
        ydb_database=ydb_database,
        ydb_sa_json_credentials=ydb_sa_json_credentials,
        ydb_sa_key_file=ydb_sa_key_file,
        log=log,
    )
    return planner, source_task_repository

"""Group-query task loading helper extracted from index entrypoint."""

from __future__ import annotations

from typing import Any, Callable


def load_work_tasks_for_group_query(
    *,
    key_json: str,
    sheet_info: dict[str, str],
    app_cfg: Any,
    build_planner_dependencies: Callable[..., Any],
) -> list[Any]:
    dependencies = build_planner_dependencies(
        key_json,
        sheet_info,
        dry_run=True,
        mock_external=True,
        cfg=app_cfg,
    )
    return dependencies.task_repository.get_task_by_color_status(["work", "pre_done"])

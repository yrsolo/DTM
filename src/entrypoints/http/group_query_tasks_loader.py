"""Group-query task loading helper."""

from __future__ import annotations

from typing import Any


def load_work_tasks_for_group_query(
    *,
    key_json: str,
    sheet_info: dict[str, str],
    app_cfg: Any,
) -> list[Any]:
    from src.app.planner_bootstrap import build_planner_dependencies

    dependencies = build_planner_dependencies(
        key_json,
        sheet_info,
        dry_run=True,
        mock_external=True,
        cfg=app_cfg,
    )
    return dependencies.task_repository.get_task_by_color_status(["work", "pre_done"])

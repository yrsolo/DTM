"""Group-query task loading helper."""

from __future__ import annotations

from typing import Any

from src.entrypoints_adapters.api_v2_adapter import build_frontend_query
from src.snapshot_engine import build_snapshot_engine


def load_work_tasks_for_group_query(
    *,
    key_json: str,  # noqa: ARG001
    sheet_info: dict[str, str],  # noqa: ARG001
    app_cfg: Any,
) -> list[Any]:
    """Compatibility helper: load active tasks from snapshot engine instead of planner."""
    from src.app.context import AppContext

    ctx = AppContext(cfg=app_cfg, deps={})
    payload = build_snapshot_engine(ctx).frontend_v2(
        build_frontend_query(
            statuses=["work", "pre_done"],
            designer="",
            limit=2000,
            include_people=True,
            window_data={"enabled": False, "start": None, "end": None, "mode": "intersects"},
        )
    )
    tasks = payload.get("tasks", [])
    if isinstance(tasks, list):
        return tasks
    return []

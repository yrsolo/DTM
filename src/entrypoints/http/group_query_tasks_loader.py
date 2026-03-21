"""Group-query task loading helper."""

from __future__ import annotations

from typing import Any

from src.contexts.access_api.internal.frontend_query import build_frontend_query
from src.contexts.snapshot.module import get_query_api


def load_work_tasks_for_group_query(
    *,
    key_json: str,  # noqa: ARG001
    sheet_info: dict[str, str],  # noqa: ARG001
    app_cfg: Any,
) -> list[Any]:
    """Load active tasks for group-query flows from the canonical snapshot read-model."""
    from src.app.context import AppContext

    ctx = AppContext(cfg=app_cfg, deps={})
    payload = get_query_api(ctx).frontend_v2(
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

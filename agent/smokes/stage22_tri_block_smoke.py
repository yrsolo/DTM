"""Stage 22 tri-block parity smoke from unified task query contract."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.contexts.access_api.internal.frontend_payload_v2 import build_frontend_api_payload_v2
from src.core.task_query_adapter import build_task_query_context, query_projections, query_source_tasks
from src.core.task_query_contract import TimeWindow, milestones_in_window


def _sample_tasks() -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            id="t-1",
            name="Alpha",
            designer="Designer A",
            status="work",
            color_status="work",
            brand="Brand A",
            format_="video",
            project_name="Project A",
            customer="Customer A",
            raw_timing="",
            timing={
                pd.Timestamp("2026-03-05"): ["раскадровка"],
                pd.Timestamp("2026-03-10"): ["аниматик"],
            },
        ),
        SimpleNamespace(
            id="t-2",
            name="Beta",
            designer="Designer B",
            status="pre_done",
            color_status="pre_done",
            brand="Brand B",
            format_="video",
            project_name="Project B",
            customer="Customer B",
            raw_timing="",
            timing={
                pd.Timestamp("2026-03-07"): ["финал"],
            },
        ),
        SimpleNamespace(
            id="t-3",
            name="Gamma",
            designer="Designer C",
            status="done",
            color_status="done",
            brand="Brand C",
            format_="video",
            project_name="Project C",
            customer="Customer C",
            raw_timing="",
            timing={
                pd.Timestamp("2026-04-15"): ["эфир"],
            },
        ),
    ]


def build_tri_block_snapshot() -> dict[str, object]:
    tasks = _sample_tasks()
    statuses = ["work", "pre_done"]
    window = TimeWindow(start=date(2026, 3, 1), end=date(2026, 3, 31), mode="intersects")

    query_context = build_task_query_context(tasks)
    render_tasks = query_source_tasks(query_context, statuses=statuses, window=window, limit=100)
    projections = query_projections(query_context, statuses=statuses, window=window, limit=100)
    notify_task_ids = sorted(
        {
            item.task_id
            for item in projections
            if milestones_in_window(item, TimeWindow(start=date(2026, 3, 5), end=date(2026, 3, 10), mode="intersects"))
        }
    )
    api_payload = build_frontend_api_payload_v2(
        tasks=tasks,
        people=[],
        env_name="test",
        source_sheet_name="stage22-smoke",
        statuses=statuses,
        limit=100,
        include_people=False,
        window_start=window.start,
        window_end=window.end,
        window_mode=window.mode,
    )
    api_task_ids = sorted([str(item.get("id", "")) for item in api_payload.get("tasks", []) if str(item.get("id", ""))])
    render_task_ids = sorted([str(getattr(item, "id", "")) for item in render_tasks if str(getattr(item, "id", ""))])

    return {
        "api_task_ids": api_task_ids,
        "render_task_ids": render_task_ids,
        "notify_task_ids": notify_task_ids,
    }


def run() -> None:
    snapshot = build_tri_block_snapshot()
    assert snapshot["api_task_ids"] == snapshot["render_task_ids"], snapshot
    assert snapshot["notify_task_ids"] == ["t-1", "t-2"], snapshot
    print(
        "stage22_tri_block_smoke_ok "
        f"api_task_ids={snapshot['api_task_ids']} "
        f"render_task_ids={snapshot['render_task_ids']} "
        f"notify_task_ids={snapshot['notify_task_ids']}"
    )


if __name__ == "__main__":
    run()



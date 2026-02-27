"""Application-layer use-cases for planner runtime orchestration."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


def resolve_run_mode(
    mode: str | None = None,
    event: Any = None,
    triggers: Mapping[str, str] | None = None,
) -> str:
    """Resolve execution mode from explicit argument or cloud trigger payload."""
    if mode:
        return mode

    if event:
        print(f"{event=}")
        if event == "morning":
            return "morning"
        trigger_id = event["messages"][0]["details"]["trigger_id"]
        resolved_mode = (triggers or {}).get(trigger_id, "test")
        print(f"{trigger_id=}")
        return resolved_mode

    return "test"


async def run_planner_use_case(planner: Any, mode: str) -> dict[str, Any]:
    """Execute planner branches for the resolved mode."""
    if mode in {"timer", "test", "sync-only"}:
        start_time = pd.Timestamp.now()
        planner.update()
        planner.task_to_calendar()
        planner.designer_task_to_calendar()
        planner.task_to_table()
        run_time = pd.Timestamp.now() - start_time
        print(f"Table update runtime: {run_time}")

    if mode in {"morning", "test", "reminders-only"}:
        start_time = pd.Timestamp.now()
        now = pd.Timestamp.now(tz="Europe/Moscow")
        dow = now.dayofweek
        if dow in {0, 1, 2, 3, 4} or mode == "test":
            await planner.send_reminders()
        run_time = pd.Timestamp.now() - start_time
        print(f"Reminder runtime: {run_time}")

    return planner.build_quality_report()

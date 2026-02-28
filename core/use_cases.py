"""Application-layer use-cases for planner runtime orchestration."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

import pandas as pd

MOSCOW_TZ = "Europe/Moscow"


class PlannerRuntimeProtocol(Protocol):
    """Planner methods required by runtime use-cases."""

    def update(self) -> None: ...

    def task_to_calendar(self) -> None: ...

    def designer_task_to_calendar(self) -> None: ...

    def task_to_table(self) -> None: ...

    async def send_reminders(self) -> None: ...

    def build_quality_report(self) -> dict[str, Any]: ...


def _resolve_mode_from_event(event: Any, triggers: Mapping[str, str] | None) -> str:
    """Resolve mode from cloud trigger payload."""

    print(f"{event=}")
    if event == "morning":
        return "morning"
    trigger_id = event["messages"][0]["details"]["trigger_id"]
    resolved_mode = (triggers or {}).get(trigger_id, "test")
    print(f"{trigger_id=}")
    return resolved_mode


def resolve_run_mode(
    mode: str | None = None,
    event: Any = None,
    triggers: Mapping[str, str] | None = None,
) -> str:
    """Resolve execution mode from explicit argument or cloud trigger payload."""
    if mode:
        return mode

    if event:
        return _resolve_mode_from_event(event, triggers)

    return "test"


async def run_planner_use_case(planner: PlannerRuntimeProtocol, mode: str) -> dict[str, Any]:
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
        now = pd.Timestamp.now(tz=MOSCOW_TZ)
        is_workday = now.dayofweek in {0, 1, 2, 3, 4}
        if is_workday or mode == "test":
            await planner.send_reminders()
        run_time = pd.Timestamp.now() - start_time
        print(f"Reminder runtime: {run_time}")

    return planner.build_quality_report()

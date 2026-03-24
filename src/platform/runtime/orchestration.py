"""Platform-owned trigger orchestration plans."""

from __future__ import annotations

from typing import Any

from src.platform.runtime.commands.types import (
    CLEANUP_JOB_STATUSES,
    RENDER_DESIGNERS_SHEET,
    RENDER_TIMELINE_SHEET,
    SEND_REMINDERS,
    UPDATE_SNAPSHOT,
)


def resolve_trigger_mode_by_id(trigger_id: str, triggers: dict[str, str]) -> str:
    """Resolve a configured trigger id to the normalized runtime trigger mode."""

    return str(triggers.get(str(trigger_id or "").strip(), "")).strip().lower()


def handle_timer_trigger(_event: Any = None) -> list[tuple[str, dict[str, Any]]]:
    """Return the canonical timer orchestration command plan."""

    return [
        (UPDATE_SNAPSHOT, {"force_refresh": False, "dry_run": False}),
        (RENDER_TIMELINE_SHEET, {"statuses": ["work", "pre_done"], "dry_run": False}),
        (RENDER_DESIGNERS_SHEET, {"statuses": ["work", "pre_done"], "dry_run": False}),
    ]


def handle_morning_trigger(_event: Any = None) -> list[tuple[str, dict[str, Any]]]:
    """Return the canonical morning orchestration command plan."""

    return [
        (
            CLEANUP_JOB_STATUSES,
            {
                "older_than_hours": 24,
                "dry_run": False,
            },
        ),
        (
            SEND_REMINDERS,
            {
                "mode": "morning",
                "statuses": ["work", "pre_done"],
                "include_today": True,
                "include_next_workday": True,
                "force_test_chat": False,
                "mock_external": False,
            },
        )
    ]


def planned_trigger_commands(trigger_mode: str) -> list[tuple[str, dict[str, Any]]]:
    """Return the platform-owned trigger command plan for the normalized mode."""

    mode = str(trigger_mode or "").strip().lower()
    if mode == "timer":
        return handle_timer_trigger()
    if mode == "morning":
        return handle_morning_trigger()
    return []


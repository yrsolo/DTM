from __future__ import annotations

from typing import Any

from src.commands.types import (
    RENDER_DESIGNERS_SHEET,
    RENDER_TIMELINE_SHEET,
    SEND_REMINDERS,
    UPDATE_SNAPSHOT,
)


def resolve_trigger_mode_by_id(trigger_id: str, triggers: dict[str, str]) -> str:
    return str(triggers.get(str(trigger_id or "").strip(), "")).strip().lower()


def planned_trigger_commands(trigger_mode: str) -> list[tuple[str, dict[str, Any]]]:
    mode = str(trigger_mode or "").strip().lower()
    if mode == "timer":
        return [
            (UPDATE_SNAPSHOT, {"force_refresh": False, "dry_run": False}),
            (RENDER_TIMELINE_SHEET, {"statuses": ["work", "pre_done"], "dry_run": False}),
            (RENDER_DESIGNERS_SHEET, {"statuses": ["work", "pre_done"], "dry_run": False}),
        ]
    if mode == "morning":
        return [
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
    return []

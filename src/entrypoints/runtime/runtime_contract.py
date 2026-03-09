"""Standard runtime mode contract for active entrypoints."""

from __future__ import annotations

STANDARD_RUN_MODES = frozenset(
    {"timer", "morning", "test", "sync-only", "reminders-only", "reminder_v2", "render_v2"}
)


def is_legacy_mode(mode: str | None) -> bool:
    return str(mode or "").strip().lower().startswith("legacy_planner_")

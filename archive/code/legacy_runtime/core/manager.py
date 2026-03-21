"""DEPRECATED: reference-only legacy manager compatibility shims."""

from __future__ import annotations

# Compatibility re-exports for extracted runtime managers.
from core.task_timing_processor import TaskTimingProcessor, get_date_range
from archive.code.legacy_runtime.services.calendar_runtime import CalendarManager, TaskCalendarManager
from archive.code.legacy_runtime.services.render.task_table_runtime import TaskManager

__all__ = [
    "TaskManager",
    "TaskTimingProcessor",
    "CalendarManager",
    "TaskCalendarManager",
    "get_date_range",
]


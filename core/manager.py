"""Manager compatibility shims."""

from __future__ import annotations

# Compatibility re-exports for extracted runtime managers.
from core.task_timing_processor import TaskTimingProcessor, get_date_range
from src.services.calendar_runtime import CalendarManager, TaskCalendarManager
from src.services.render.task_table_runtime import TaskManager

__all__ = [
    "TaskManager",
    "TaskTimingProcessor",
    "CalendarManager",
    "TaskCalendarManager",
    "get_date_range",
]

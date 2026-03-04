"""Task repository contracts and compatibility shims."""

from __future__ import annotations

from core.models.task import Task
from core.task_repository_contract import TaskRepository
from core.timing_parser import TimingParser


# Compatibility shims for legacy imports.
from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository

__all__ = ["Task", "TaskRepository", "GoogleSheetsTaskRepository", "TimingParser"]

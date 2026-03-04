"""Task repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.task import Task


class TaskRepository(ABC):
    """Base task repository contract."""

    @abstractmethod
    def get_all_tasks(self) -> list[Task]:
        raise NotImplementedError

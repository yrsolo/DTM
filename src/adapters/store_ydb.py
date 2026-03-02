"""Operational store adapter boundary.

Current migration implementation provides a JSON-backed adapter as minimal
operational store for M4 before YDB wiring.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonOperationalStore:
    """Minimal JSON-backed upsert store for normalized records."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"tasks": {}}
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Upsert tasks by `task_id` and return updated payload."""
        store = self.load()
        tasks_map = store.setdefault("tasks", {})
        for task in tasks:
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                continue
            tasks_map[task_id] = task
        self.save(store)
        return store


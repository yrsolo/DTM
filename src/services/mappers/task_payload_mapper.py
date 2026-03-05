"""Task payload mapping used by timer pipeline."""

from __future__ import annotations

from typing import Any


class TaskPayloadMapper:
    """Map normalized task objects into operational YDB payloads."""

    def to_operational_payload(self, task: Any) -> dict[str, object]:
        milestones = []
        for idx, (dt, stages) in enumerate(sorted(task.timing.items(), key=lambda item: item[0])):
            planned = dt.date().isoformat()
            for stage in stages:
                milestones.append(
                    {
                        "idx": idx,
                        "type": str(stage).strip().lower() or "unknown",
                        "planned": planned,
                        "actual": None,
                        "status": "planned",
                        "raw_text": str(stage),
                    }
                )

        start_date = task.min_date.date().isoformat() if task.min_date is not None else None
        end_date = task.max_date.date().isoformat() if task.max_date is not None else None
        next_due_date = task.min_date.date().isoformat() if task.min_date is not None else None
        task_hash_basis = {
            "id": str(task.id),
            "name": task.name,
            "brand": task.brand,
            "format_": task.format_,
            "project_name": task.project_name,
            "customer": task.customer,
            "designer": task.designer,
            "history": task.status,
            "raw_status": task.status,
            "status": task.color_status,
            "raw_timing": task.raw_timing,
            "milestones": milestones,
        }

        return {
            "task_id": str(task.id),
            "title": task.name,
            "brand": task.brand,
            "format_": task.format_,
            "customer": task.customer,
            "raw_timing": task.raw_timing,
            "history": task.status,
            "raw_status": task.status,
            "owner_id": task.designer,
            "group_id": task.project_name,
            "status": task.color_status,
            "start_date": start_date,
            "end_date": end_date,
            "next_due_date": next_due_date,
            "tags": [],
            "links": {},
            "task_hash": None,
            "task_revision": 0,
            "raw_payload": task_hash_basis,
            "milestones": milestones,
        }

"""HTTP API payload builder for frontend consumers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

import pandas as pd

from core.people import Person
from core.repository import Task
from core.task_query_adapter import build_task_query_context, query_projections
from core.task_query_contract import TimeWindow


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_str(value: Any) -> str:
    return str(value or "").strip()


def _serialize_task(task: Any, today: pd.Timestamp) -> dict[str, Any]:
    _ = today
    timing_rows = sorted(task.timing.items(), key=lambda item: item[0])
    next_due = task.next_due
    return {
        "id": str(task.task_id),
        "name": _to_str(task.title),
        "designer": _to_str(task.designer),
        "status": _to_str(task.status),
        "color_status": _to_str(task.color_status),
        "brand": _to_str(task.brand),
        "format": _to_str(task.format_),
        "project_name": _to_str(task.project_name),
        "customer": _to_str(task.customer),
        "min_date": task.min_date.strftime("%Y-%m-%d") if task.min_date is not None else None,
        "max_date": task.max_date.strftime("%Y-%m-%d") if task.max_date is not None else None,
        "next_due_date": next_due.strftime("%Y-%m-%d") if next_due is not None else None,
        "timing": [
            {
                "date": date.strftime("%Y-%m-%d"),
                "stages": [str(stage) for stage in stages],
            }
            for date, stages in timing_rows
        ],
    }


def _serialize_person(person: Person) -> dict[str, Any]:
    return {
        "id": _to_str(person.id),
        "name": _to_str(person.name),
        "position": _to_str(person.position),
        "vacation": _to_str(person.vacation),
        "telegram_id": _to_str(person.telegram_id),
        "chat_id": _to_str(person.chat_id),
    }


def _build_deadlines(tasks: list[Any], today: pd.Timestamp, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        due_date = task.next_due
        if due_date is None:
            continue
        stages = task.timing.get(due_date, [])
        rows.append(
            {
                "date": due_date.strftime("%Y-%m-%d"),
                "task_id": str(task.task_id),
                "task_name": _to_str(task.title),
                "designer": _to_str(task.designer),
                "stages": [str(stage) for stage in stages],
            }
        )
    rows.sort(key=lambda item: item["date"])
    return rows[: max(limit, 0)]


def build_frontend_api_payload(
    tasks: Iterable[Task],
    people: Iterable[Person],
    *,
    env_name: str,
    source_sheet_name: str,
    statuses: list[str],
    limit: int,
    include_people: bool,
    designer_filter: str = "",
) -> dict[str, Any]:
    """Build deterministic frontend payload for HTTP API."""
    today = pd.Timestamp.today().normalize()
    query_context = build_task_query_context(tasks)
    task_list = query_context.projections
    tasks_filtered = query_projections(
        query_context,
        statuses=statuses,
        designer=designer_filter,
        limit=10**9,
        window=TimeWindow(),
    )
    tasks_limited = tasks_filtered[: max(limit, 0)]
    task_payload = [_serialize_task(task, today) for task in tasks_limited]

    payload: dict[str, Any] = {
        "artifact": "dtm_frontend_api_payload",
        "generated_at_utc": _now_utc_iso(),
        "source": {
            "env": env_name,
            "source_sheet_name": source_sheet_name,
        },
        "filters": {
            "statuses": statuses,
            "designer": _to_str(designer_filter),
            "limit": limit,
            "include_people": include_people,
        },
        "summary": {
            "tasks_total": len(task_list),
            "tasks_filtered": len(tasks_filtered),
            "tasks_returned": len(task_payload),
        },
        "tasks": task_payload,
        "deadlines": _build_deadlines(tasks_filtered, today=today, limit=min(limit, 50)),
    }
    if include_people:
        people_list = list(people)
        payload["people"] = [_serialize_person(person) for person in people_list]
        payload["summary"]["people_total"] = len(people_list)
    return payload

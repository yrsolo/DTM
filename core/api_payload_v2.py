"""Frontend API v2 payload builder."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable

import pandas as pd

from core.people import Person
from core.repository import Task


def _utc_iso(dt: datetime | None = None) -> str:
    value = dt or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_str(value: Any) -> str:
    return str(value or "").strip()


def _stable_id(prefix: str, value: str) -> str:
    payload = f"{prefix}:{value}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def _owner_id(task: Task) -> str:
    raw = _to_str(task.designer)
    return _stable_id("owner", raw) if raw else "owner:unassigned"


def _group_id(task: Task) -> str:
    raw = _to_str(task.project_name)
    return _stable_id("group", raw) if raw else "group:default"


def _task_due_date(task: Task, today: pd.Timestamp) -> pd.Timestamp | None:
    future_dates = [date for date in task.timing.keys() if date >= today]
    if future_dates:
        return min(future_dates)
    return task.max_date


def _serialize_task(task: Task, today: pd.Timestamp) -> dict[str, Any]:
    due = _task_due_date(task, today)
    start = task.min_date.strftime("%Y-%m-%d") if task.min_date is not None else None
    end = task.max_date.strftime("%Y-%m-%d") if task.max_date is not None else None
    next_due = due.strftime("%Y-%m-%d") if due is not None else None
    return {
        "id": str(task.id),
        "title": _to_str(task.name),
        "ownerId": _owner_id(task),
        "groupId": _group_id(task),
        "status": _to_str(task.color_status or task.status or "unknown"),
        "date": {
            "start": start,
            "end": end,
            "nextDue": next_due,
        },
        "tags": [],
        "hash": None,
        "revision": None,
        "links": {
            "sheetRowUrl": None,
            "self": f"/api/v2/frontend/tasks/{task.id}",
        },
    }


def _serialize_people(people: Iterable[Person]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for person in people:
        person_id = _to_str(person.id) or _stable_id("person", _to_str(person.name))
        if person_id in result:
            continue
        result[person_id] = {
            "id": person_id,
            "name": _to_str(person.name),
            "position": _to_str(person.position) or None,
            "links": {
                "self": f"/api/v2/frontend/entities/people/{person_id}",
            },
        }
    return sorted(result.values(), key=lambda item: item["id"])


def _serialize_groups(tasks: Iterable[Task]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for task in tasks:
        gid = _group_id(task)
        if gid in result:
            continue
        result[gid] = {
            "id": gid,
            "name": _to_str(task.project_name) or "Default",
            "links": {
                "self": f"/api/v2/frontend/entities/groups/{gid}",
            },
        }
    return sorted(result.values(), key=lambda item: item["id"])


def _stable_payload_hash(payload: dict[str, Any]) -> str:
    base = dict(payload)
    meta = dict(base.get("meta", {}))
    meta["hash"] = ""
    base["meta"] = meta
    serialized = json.dumps(base, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_frontend_api_payload_v2(
    tasks: Iterable[Task],
    people: Iterable[Person],
    *,
    env_name: str,
    source_sheet_name: str,
    statuses: list[str],
    limit: int,
    include_people: bool,
    designer_filter: str = "",
    generated_at: datetime | None = None,
    synced_at: datetime | None = None,
) -> dict[str, Any]:
    """Build v2 payload with stable hash and extensible entity model."""
    today = pd.Timestamp.today().normalize()
    items = list(tasks)

    target_designer = _to_str(designer_filter).casefold()
    if target_designer:
        items = [
            task
            for task in items
            if target_designer in {name.strip().casefold() for name in _to_str(task.designer).split("\n") if name.strip()}
        ]

    items.sort(key=lambda task: (_task_due_date(task, today) or pd.Timestamp.max, _to_str(task.name)))
    items = items[: max(limit, 0)]
    tasks_v2 = [_serialize_task(task, today) for task in items]

    people_v2 = _serialize_people(people) if include_people else []
    groups_v2 = _serialize_groups(items)

    payload: dict[str, Any] = {
        "meta": {
            "artifact": "dtm_frontend_api_v2",
            "contractVersion": "2.0.0",
            "generatedAt": _utc_iso(generated_at),
            "syncedAt": _utc_iso(synced_at),
            "source": {
                "env": env_name,
                "sourceId": source_sheet_name,
                "sheetName": source_sheet_name,
                "sheetUrl": None,
            },
            "hash": "",
            "features": {
                "taskHash": True,
                "taskRevision": True,
                "entities": True,
            },
            "paging": {
                "limit": limit,
                "nextCursor": None,
            },
        },
        "filters": {
            "statuses": statuses,
            "designer": _to_str(designer_filter),
            "limit": limit,
            "includePeople": include_people,
        },
        "summary": {
            "tasksReturned": len(tasks_v2),
            "peopleReturned": len(people_v2),
            "groupsReturned": len(groups_v2),
        },
        "entities": {
            "people": people_v2,
            "groups": groups_v2,
            "tags": [],
            "enums": {
                "status": {
                    "work": "In work",
                    "pre_done": "Pre done",
                    "wait": "Waiting",
                    "done": "Done",
                },
                "statusGroups": {
                    "active": ["work", "pre_done"],
                    "final": ["done"],
                },
            },
        },
        "tasks": tasks_v2,
    }
    payload["meta"]["hash"] = _stable_payload_hash(payload)
    return payload

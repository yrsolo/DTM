"""Frontend API v2 payload builder."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
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


def _normalize_milestone_type(stage_name: str) -> tuple[str, str]:
    value = _to_str(stage_name).lower()
    mapping: list[tuple[str, str, str]] = [
        ("storyboard", "раскадров", "раскадровка"),
        ("animatic", "анимат", "аниматик"),
        ("prefinal", "префинал", "префинал"),
        ("final", "финал", "финал"),
        ("onair", "эфир", "эфир"),
        ("feedback", "ответ", "ответ"),
        ("draft", "драфт", "драфт"),
    ]
    for type_id, marker, label in mapping:
        if marker in value:
            return type_id, label
    compact = re.sub(r"\s+", " ", _to_str(stage_name)).strip()
    if compact:
        return f"stage_{hashlib.sha1(compact.encode('utf-8')).hexdigest()[:8]}", compact.lower()
    return "unknown_stage", "неизвестный этап"


def _infer_milestone_status(stage_name: str) -> str:
    value = _to_str(stage_name).lower()
    if not value:
        return "unknown"
    if any(marker in value for marker in ("skip", "пропуск", "отмен", "не делаем")):
        return "skipped"
    if any(marker in value for marker in ("done", "готов", "сдан", "утвержд")):
        return "done"
    return "planned"


def _serialize_milestones(task: Task) -> tuple[list[dict[str, Any]], dict[str, str]]:
    milestones: list[dict[str, Any]] = []
    milestone_labels: dict[str, str] = {}
    for timing_date, stages in task.timing.items():
        planned = timing_date.strftime("%Y-%m-%d") if isinstance(timing_date, pd.Timestamp) else None
        for stage in stages:
            stage_text = _to_str(stage)
            milestone_type, label = _normalize_milestone_type(stage_text)
            milestone_labels[milestone_type] = label
            milestones.append(
                {
                    "type": milestone_type,
                    "planned": planned,
                    "actual": None,
                    "status": _infer_milestone_status(stage_text),
                }
            )

    milestones.sort(key=lambda item: (item["planned"] is None, item["planned"] or "9999-99-99", item["type"]))
    return milestones, milestone_labels


def _task_matches_window(task: Task, window_start: date, window_end: date) -> bool:
    start = task.min_date.date() if task.min_date is not None else None
    end = task.max_date.date() if task.max_date is not None else None
    if start is None and end is None:
        return False
    if start is not None and window_start <= start <= window_end:
        return True
    if end is not None and window_start <= end <= window_end:
        return True
    return False


def _serialize_task(task: Task, today: pd.Timestamp) -> dict[str, Any]:
    due = _task_due_date(task, today)
    start = task.min_date.strftime("%Y-%m-%d") if task.min_date is not None else None
    end = task.max_date.strftime("%Y-%m-%d") if task.max_date is not None else None
    next_due = due.strftime("%Y-%m-%d") if due is not None else None
    milestones, milestone_labels = _serialize_milestones(task)
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
        "milestones": milestones,
        "_milestone_labels": milestone_labels,
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
    window_start: date | None = None,
    window_end: date | None = None,
    window_mode: str = "intersects",
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

    tasks_total = len(items)
    window_enabled = window_start is not None and window_end is not None
    if window_enabled and window_mode == "intersects":
        items = [task for task in items if _task_matches_window(task, window_start, window_end)]

    items.sort(key=lambda task: (_task_due_date(task, today) or pd.Timestamp.max, _to_str(task.name)))
    items = items[: max(limit, 0)]
    tasks_v2 = [_serialize_task(task, today) for task in items]
    milestone_type_labels: dict[str, str] = {}
    for task_payload in tasks_v2:
        for type_id, label in task_payload.pop("_milestone_labels", {}).items():
            milestone_type_labels[type_id] = label

    people_v2 = _serialize_people(people) if include_people else []
    groups_v2 = _serialize_groups(items)
    milestones_total = sum(len(task_payload.get("milestones", [])) for task_payload in tasks_v2)

    payload: dict[str, Any] = {
        "meta": {
            "artifact": "dtm_frontend_api_v2",
            "contractVersion": "2.0.1",
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
                "milestonesDefault": True,
                "timeWindowFilter": True,
            },
            "paging": {
                "limit": limit,
                "nextCursor": None,
            },
        },
        "filters": {
            "statuses": statuses,
            "designer": _to_str(designer_filter) or None,
            "limit": limit,
            "include_people": include_people,
            "window": {
                "enabled": window_enabled,
                "start": window_start.isoformat() if window_start else None,
                "end": window_end.isoformat() if window_end else None,
                "mode": window_mode or "intersects",
            },
        },
        "summary": {
            "tasksTotal": tasks_total,
            "tasksReturned": len(tasks_v2),
            "peopleTotal": len(people_v2),
            "groupsTotal": len(groups_v2),
            "milestonesTotal": milestones_total,
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
                "milestoneType": dict(sorted(milestone_type_labels.items())),
                "milestoneStatus": {
                    "planned": "Запланировано",
                    "done": "Готово",
                    "unknown": "Неизвестно",
                    "skipped": "Пропущено",
                },
            },
        },
        "tasks": tasks_v2,
    }
    payload["meta"]["hash"] = _stable_payload_hash(payload)
    return payload

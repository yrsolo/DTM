"""Frontend API v2 payload builder."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from datetime import datetime, timezone
from typing import Any, Iterable

from core.models.people import Person
from core.task_query_adapter import TaskQueryContext, build_task_query_context, query_projections
from core.task_query_contract import TimeWindow, milestone_type_labels


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


def _owner_id(task: Any) -> str:
    raw = _to_str(task.designer)
    return _stable_id("owner", raw) if raw else "owner:unassigned"


def _group_id(task: Any) -> str:
    raw = _to_str(task.project_name)
    return _stable_id("group", raw) if raw else "group:default"


def _serialize_task(task: Any) -> dict[str, Any]:
    start = task.min_date.strftime("%Y-%m-%d") if task.min_date is not None else None
    end = task.max_date.strftime("%Y-%m-%d") if task.max_date is not None else None
    next_due = task.next_due.strftime("%Y-%m-%d") if task.next_due is not None else None
    milestones = [
        {
            "type": item.type,
            "planned": item.planned.isoformat() if item.planned is not None else None,
            "actual": item.actual.isoformat() if item.actual is not None else None,
            "status": item.status,
        }
        for item in task.milestones
    ]
    date_payload = {
        "start": start,
        "end": end,
        "nextDue": next_due,
    }
    # Keep only known dates to reduce noisy null-heavy responses.
    date_payload = {key: value for key, value in date_payload.items() if value is not None}

    return {
        "id": str(task.task_id),
        "title": _to_str(task.title),
        "brand": _to_str(getattr(task, "brand", "")),
        "format_": _to_str(getattr(task, "format_", "")),
        "customer": _to_str(getattr(task, "customer", "")),
        "history": _to_str(getattr(task, "history", "")),
        "ownerId": _owner_id(task),
        "groupId": _group_id(task),
        "status": _to_str(task.color_status or task.status or "unknown"),
        "date": date_payload,
        "tags": [],
        "links": {
            "self": f"/api/v2/frontend/tasks/{task.task_id}",
        },
        "milestones": milestones,
    }


def _person_id(person: Person) -> str:
    # Keep person id stable and aligned with task owner ids.
    seed = _to_str(person.name) or _to_str(person.id)
    return _stable_id("owner", seed) if seed else "owner:unassigned"


def _build_owner_lookup(people: Iterable[Person]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for person in people:
        pid = _person_id(person)
        pname = _to_str(person.name)
        if pname:
            lookup[pname.casefold()] = pid
        if pid:
            lookup[pid.casefold()] = pid
    return lookup


def _resolve_owner_id(task: Any, owner_lookup: dict[str, str]) -> str:
    raw = _to_str(task.designer)
    if raw:
        mapped = owner_lookup.get(raw.casefold())
        if mapped:
            return mapped
    return _owner_id(task)


def _serialize_task_with_owner(task: Any, owner_lookup: dict[str, str]) -> dict[str, Any]:
    payload = _serialize_task(task)
    payload["ownerId"] = _resolve_owner_id(task, owner_lookup)
    return payload


def _serialize_people(people: Iterable[Person]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for person in people:
        person_id = _person_id(person)
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


def _serialize_groups(tasks: Iterable[Any]) -> list[dict[str, Any]]:
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
    tasks: Iterable[Any],
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
    query_context = build_task_query_context(tasks)
    pre_window_filtered = query_projections(
        query_context,
        statuses=statuses,
        designer=designer_filter,
        limit=10**9,
        window=TimeWindow(),
    )
    tasks_total = len(pre_window_filtered)
    query_window = TimeWindow(start=window_start, end=window_end, mode=window_mode or "intersects")
    filtered = query_projections(
        TaskQueryContext(projections=list(pre_window_filtered)),
        limit=max(limit, 0),
        window=query_window,
    )
    people_list = list(people)
    owner_lookup = _build_owner_lookup(people_list)
    tasks_v2 = [_serialize_task_with_owner(item, owner_lookup) for item in filtered]
    milestone_types = milestone_type_labels(filtered)

    people_v2 = _serialize_people(people_list) if include_people else []
    groups_v2 = _serialize_groups(filtered)
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
                "sheetUrl": "",
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
                "nextCursor": "",
            },
        },
        "filters": {
            "statuses": statuses,
            "designer": _to_str(designer_filter),
            "limit": limit,
            "include_people": include_people,
            "window": {
                "enabled": query_window.enabled,
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
                "milestoneType": dict(sorted(milestone_types.items())),
                "milestoneStatus": {
                    "planned": "Planned",
                    "done": "Done",
                    "unknown": "Unknown",
                    "skipped": "Skipped",
                },
            },
        },
        "tasks": tasks_v2,
    }
    payload["meta"]["hash"] = _stable_payload_hash(payload)
    return payload

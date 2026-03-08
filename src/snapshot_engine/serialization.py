"""JSON serialization helpers for snapshot engine models."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any

from src.snapshot_engine.model import (
    Milestone,
    PeopleSnapshot,
    PersonView,
    PrepIndexes,
    PrepSnapshot,
    RawSnapshot,
    TaskExtra,
    TaskSheet,
    TaskView,
)


def _dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    target = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return target.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _milestone_to_dict(item: Milestone) -> dict[str, Any]:
    return {
        "type": item.type,
        "planned": item.planned.isoformat() if item.planned is not None else None,
        "actual": item.actual.isoformat() if item.actual is not None else None,
        "status": item.status,
    }


def _milestone_from_dict(item: dict[str, Any]) -> Milestone:
    return Milestone(
        type=str(item.get("type", "")).strip() or "unknown",
        planned=_parse_date(item.get("planned")),
        actual=_parse_date(item.get("actual")),
        status=str(item.get("status", "planned")).strip() or "planned",
    )


def raw_to_dict(raw: RawSnapshot) -> dict[str, Any]:
    tasks = {}
    for task_id, task in raw.tasks_by_id.items():
        tasks[task_id] = {
            "task_id": task.task_id,
            "title": task.title,
            "owner_id": task.owner_id,
            "group_id": task.group_id,
            "brand": task.brand,
            "format_": task.format_,
            "customer": task.customer,
            "raw_timing": task.raw_timing,
            "status": task.status,
            "history": task.history,
            "timing": task.timing,
            "milestones": [_milestone_to_dict(item) for item in task.milestones],
        }
    return {
        "source_id": raw.source_id,
        "source_hash": raw.source_hash,
        "fetched_at_utc": _dt(raw.fetched_at_utc),
        "tasks_by_id": tasks,
    }


def raw_from_dict(payload: dict[str, Any]) -> RawSnapshot:
    tasks_by_id: dict[str, TaskSheet] = {}
    for task_id, item in dict(payload.get("tasks_by_id", {})).items():
        if not isinstance(item, dict):
            continue
        tasks_by_id[str(task_id)] = TaskSheet(
            task_id=str(item.get("task_id", task_id)).strip(),
            title=str(item.get("title", "")).strip(),
            owner_id=str(item.get("owner_id", "")).strip(),
            group_id=str(item.get("group_id", "")).strip(),
            brand=str(item.get("brand", "")).strip(),
            format_=str(item.get("format_", "")).strip(),
            customer=str(item.get("customer", "")).strip(),
            raw_timing=str(item.get("raw_timing", "")).strip(),
            status=str(item.get("status", "")).strip() or "unknown",
            history=str(item.get("history", "")).strip(),
            timing={
                str(key): [str(stage) for stage in list(value or [])]
                for key, value in dict(item.get("timing", {})).items()
            },
            milestones=[_milestone_from_dict(m) for m in list(item.get("milestones", [])) if isinstance(m, dict)],
        )
    return RawSnapshot(
        source_id=str(payload.get("source_id", "")).strip(),
        source_hash=str(payload.get("source_hash", "")).strip(),
        fetched_at_utc=_parse_dt(payload.get("fetched_at_utc")) or datetime.now(timezone.utc),
        tasks_by_id=tasks_by_id,
    )


def prep_to_dict(prep: PrepSnapshot) -> dict[str, Any]:
    tasks = {}
    for task_id, view in prep.tasks_by_id.items():
        tasks[task_id] = {
            "sheet": raw_to_dict(
                RawSnapshot(
                    source_id=prep.source_id,
                    source_hash=prep.raw_source_hash,
                    fetched_at_utc=prep.built_at_utc,
                    tasks_by_id={task_id: view.sheet},
                )
            )["tasks_by_id"][task_id],
            "extra": extra_to_dict(view.extra) if view.extra is not None else None,
        }
    return {
        "source_id": prep.source_id,
        "raw_source_hash": prep.raw_source_hash,
        "built_at_utc": _dt(prep.built_at_utc),
        "tasks_by_id": tasks,
        "indexes": {
            "by_status": prep.indexes.by_status,
            "by_owner": prep.indexes.by_owner,
        },
    }


def prep_from_dict(payload: dict[str, Any]) -> PrepSnapshot:
    tasks_by_id: dict[str, TaskView] = {}
    tasks_raw = dict(payload.get("tasks_by_id", {}))
    for task_id, item in tasks_raw.items():
        if not isinstance(item, dict):
            continue
        sheet_payload = item.get("sheet", {})
        if not isinstance(sheet_payload, dict):
            continue
        sheet = raw_from_dict(
            {
                "source_id": payload.get("source_id", ""),
                "source_hash": payload.get("raw_source_hash", ""),
                "fetched_at_utc": payload.get("built_at_utc"),
                "tasks_by_id": {task_id: sheet_payload},
            }
        ).tasks_by_id[str(task_id)]
        extra_payload = item.get("extra")
        extra = extra_from_dict(extra_payload) if isinstance(extra_payload, dict) else None
        tasks_by_id[str(task_id)] = TaskView(sheet=sheet, extra=extra)
    indexes_payload = payload.get("indexes", {}) if isinstance(payload.get("indexes", {}), dict) else {}
    return PrepSnapshot(
        source_id=str(payload.get("source_id", "")).strip(),
        raw_source_hash=str(payload.get("raw_source_hash", "")).strip(),
        built_at_utc=_parse_dt(payload.get("built_at_utc")) or datetime.now(timezone.utc),
        tasks_by_id=tasks_by_id,
        indexes=PrepIndexes(
            by_status={str(k): [str(v) for v in list(vals or [])] for k, vals in dict(indexes_payload.get("by_status", {})).items()},
            by_owner={str(k): [str(v) for v in list(vals or [])] for k, vals in dict(indexes_payload.get("by_owner", {})).items()},
        ),
    )


def people_to_dict(snapshot: PeopleSnapshot) -> dict[str, Any]:
    people: dict[str, dict[str, Any]] = {}
    for key, person in snapshot.people_by_name.items():
        people[str(key)] = {
            "name": str(person.name),
            "chat_id": str(person.chat_id),
            "vacation": str(person.vacation),
            "position": str(person.position),
            "person_id": str(person.person_id),
        }
    return {
        "source_id": str(snapshot.source_id),
        "fetched_at_utc": _dt(snapshot.fetched_at_utc),
        "people_by_name": people,
    }


def people_from_dict(payload: dict[str, Any]) -> PeopleSnapshot:
    people_raw = payload.get("people_by_name", {})
    people_by_name: dict[str, PersonView] = {}
    if isinstance(people_raw, dict):
        for key, item in people_raw.items():
            if not isinstance(item, dict):
                continue
            people_by_name[str(key)] = PersonView(
                name=str(item.get("name", "")).strip(),
                chat_id=str(item.get("chat_id", "")).strip(),
                vacation=str(item.get("vacation", "")).strip(),
                position=str(item.get("position", "")).strip(),
                person_id=str(item.get("person_id", "")).strip(),
            )
    return PeopleSnapshot(
        source_id=str(payload.get("source_id", "")).strip(),
        fetched_at_utc=_parse_dt(payload.get("fetched_at_utc")) or datetime.now(timezone.utc),
        people_by_name=people_by_name,
    )


def extra_to_dict(extra: TaskExtra) -> dict[str, Any]:
    return {
        "task_id": extra.task_id,
        "orphaned": bool(extra.orphaned),
        "updated_at_utc": _dt(extra.updated_at_utc),
        "docs": list(extra.docs),
        "links": list(extra.links),
        "notes": extra.notes,
        "artifacts": list(extra.artifacts),
    }


def extra_from_dict(payload: dict[str, Any]) -> TaskExtra:
    return TaskExtra(
        task_id=str(payload.get("task_id", "")).strip(),
        orphaned=bool(payload.get("orphaned", False)),
        updated_at_utc=_parse_dt(payload.get("updated_at_utc")),
        docs=[dict(item) for item in list(payload.get("docs", [])) if isinstance(item, dict)],
        links=[str(item) for item in list(payload.get("links", []))],
        notes=str(payload.get("notes", "")),
        artifacts=[dict(item) for item in list(payload.get("artifacts", [])) if isinstance(item, dict)],
    )


def dumps_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def loads_json(text: str) -> dict[str, Any]:
    payload = json.loads(text or "{}")
    if not isinstance(payload, dict):
        raise ValueError("snapshot payload must be a JSON object")
    return payload

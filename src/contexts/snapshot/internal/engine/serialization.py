"""JSON serialization helpers for snapshot engine models."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any

from src.contexts.snapshot.internal.engine.model import (
    AttachmentMeta,
    ExtraSnapshot,
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


def _attachment_to_dict(item: AttachmentMeta) -> dict[str, Any]:
    return {
        "attachment_id": str(item.attachment_id),
        "task_id": str(item.task_id),
        "filename_original": str(item.filename_original),
        "filename_display": str(item.filename_display),
        "mime_type": str(item.mime_type),
        "kind": str(item.kind),
        "size_bytes": int(item.size_bytes),
        "storage_bucket": str(item.storage_bucket),
        "storage_key": str(item.storage_key),
        "storage_etag": str(item.storage_etag),
        "storage_version": str(item.storage_version),
        "sha256": str(item.sha256),
        "status": str(item.status),
        "uploaded_by_user_id": str(item.uploaded_by_user_id),
        "uploaded_at": _dt(item.uploaded_at_utc),
        "verified_at": _dt(item.verified_at_utc),
        "deleted_at": _dt(item.deleted_at_utc),
        "deleted_by_user_id": str(item.deleted_by_user_id),
        "error_code": str(item.error_code),
        "error_message": str(item.error_message),
        "snapshot_visible": bool(item.snapshot_visible),
        "preview_capabilities": list(item.preview_capabilities or []),
        "sort_key": str(item.sort_key),
        "preview": str(item.preview),
        "summary_status": str(item.summary_status),
        "summary_text": str(item.summary_text),
        "summary_model": str(item.summary_model),
        "summary_version": str(item.summary_version),
        "summary_generated_at": _dt(item.summary_generated_at_utc),
        "extracted_text_status": str(item.extracted_text_status),
        "extracted_text_ref": str(item.extracted_text_ref),
        "detected_language": str(item.detected_language),
        "page_count": item.page_count,
        "image_width": item.image_width,
        "image_height": item.image_height,
        "preview_state": str(item.preview_state),
        "derived_preview_ref": str(item.derived_preview_ref),
        "classification": dict(item.classification or {}),
        "tags": list(item.tags or []),
        "warnings": list(item.warnings or []),
        "custom_meta": dict(item.custom_meta or {}),
    }


def _attachment_from_dict(item: dict[str, Any]) -> AttachmentMeta:
    return AttachmentMeta(
        id=str(item.get("id", item.get("attachment_id", ""))).strip(),
        key=str(item.get("key", item.get("storage_key", ""))).strip(),
        filename=str(item.get("filename", item.get("filename_display", item.get("filename_original", "")))).strip(),
        mime=str(item.get("mime", item.get("mime_type", ""))).strip(),
        size=max(int(item.get("size", item.get("size_bytes", 0)) or 0), 0),
        uploaded_at_utc=_parse_dt(item.get("uploaded_at")) or datetime.now(timezone.utc),
        uploaded_by=str(item.get("uploaded_by", item.get("uploaded_by_user_id", ""))).strip(),
        preview=str(item.get("preview", "")).strip(),
        task_id=str(item.get("task_id", "")).strip(),
        attachment_id=str(item.get("attachment_id", item.get("id", ""))).strip(),
        filename_original=str(item.get("filename_original", item.get("filename", ""))).strip(),
        filename_display=str(item.get("filename_display", item.get("filename", ""))).strip(),
        mime_type=str(item.get("mime_type", item.get("mime", ""))).strip(),
        kind=str(item.get("kind", "")).strip(),
        size_bytes=max(int(item.get("size_bytes", item.get("size", 0)) or 0), 0),
        storage_bucket=str(item.get("storage_bucket", "")).strip(),
        storage_key=str(item.get("storage_key", item.get("key", ""))).strip(),
        storage_etag=str(item.get("storage_etag", "")).strip(),
        storage_version=str(item.get("storage_version", "")).strip(),
        sha256=str(item.get("sha256", "")).strip(),
        status=str(item.get("status", "ready")).strip() or "ready",
        uploaded_by_user_id=str(item.get("uploaded_by_user_id", item.get("uploaded_by", ""))).strip(),
        verified_at_utc=_parse_dt(item.get("verified_at")),
        deleted_at_utc=_parse_dt(item.get("deleted_at")),
        deleted_by_user_id=str(item.get("deleted_by_user_id", "")).strip(),
        error_code=str(item.get("error_code", "")).strip(),
        error_message=str(item.get("error_message", "")).strip(),
        snapshot_visible=bool(item.get("snapshot_visible", True)),
        preview_capabilities=[str(value) for value in list(item.get("preview_capabilities", []) or [])],
        sort_key=str(item.get("sort_key", "")).strip(),
        summary_status=str(item.get("summary_status", "none")).strip() or "none",
        summary_text=str(item.get("summary_text", "")).strip(),
        summary_model=str(item.get("summary_model", "")).strip(),
        summary_version=str(item.get("summary_version", "")).strip(),
        summary_generated_at_utc=_parse_dt(item.get("summary_generated_at")),
        extracted_text_status=str(item.get("extracted_text_status", "none")).strip() or "none",
        extracted_text_ref=str(item.get("extracted_text_ref", "")).strip(),
        detected_language=str(item.get("detected_language", "")).strip(),
        page_count=item.get("page_count"),
        image_width=item.get("image_width"),
        image_height=item.get("image_height"),
        preview_state=str(item.get("preview_state", "none")).strip() or "none",
        derived_preview_ref=str(item.get("derived_preview_ref", "")).strip(),
        classification=dict(item.get("classification", {}) or {}),
        tags=[str(value) for value in list(item.get("tags", []) or [])],
        warnings=[str(value) for value in list(item.get("warnings", []) or [])],
        custom_meta=dict(item.get("custom_meta", {}) or {}),
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
            "is_active": bool(person.is_active),
            "chat_id": str(person.chat_id),
            "vacation": str(person.vacation),
            "position": str(person.position),
            "person_id": str(person.person_id),
            "contact_email": str(person.contact_email),
            "yandex_email": str(person.yandex_email),
            "telegram": str(person.telegram),
            "telegram_id": str(person.telegram_id),
            "info": str(person.info),
            "phone": str(person.phone),
            "attributes": {
                str(attr_key): str(attr_value)
                for attr_key, attr_value in sorted(dict(person.attributes or {}).items())
            },
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
                is_active=bool(item.get("is_active", True)),
                chat_id=str(item.get("chat_id", "")).strip(),
                vacation=str(item.get("vacation", "")).strip(),
                position=str(item.get("position", "")).strip(),
                person_id=str(item.get("person_id", "")).strip(),
                contact_email=str(item.get("contact_email", "")).strip(),
                yandex_email=str(item.get("yandex_email", "")).strip(),
                telegram=str(item.get("telegram", "")).strip(),
                telegram_id=str(item.get("telegram_id", "")).strip(),
                info=str(item.get("info", "")).strip(),
                phone=str(item.get("phone", "")).strip(),
                attributes={
                    str(attr_key): str(attr_value).strip()
                    for attr_key, attr_value in dict(item.get("attributes", {}) or {}).items()
                },
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
        "attachments": [_attachment_to_dict(item) for item in list(extra.attachments or [])],
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
        attachments=[_attachment_from_dict(item) for item in list(payload.get("attachments", [])) if isinstance(item, dict)],
        docs=[dict(item) for item in list(payload.get("docs", [])) if isinstance(item, dict)],
        links=[str(item) for item in list(payload.get("links", []))],
        notes=str(payload.get("notes", "")),
        artifacts=[dict(item) for item in list(payload.get("artifacts", [])) if isinstance(item, dict)],
    )


def extra_snapshot_to_dict(snapshot: ExtraSnapshot) -> dict[str, Any]:
    return {
        "version": int(snapshot.version),
        "updated_at_utc": _dt(snapshot.updated_at_utc),
        "items_by_task_id": {
            str(task_id): extra_to_dict(extra)
            for task_id, extra in sorted(snapshot.items_by_task_id.items())
        },
    }


def extra_snapshot_from_dict(payload: dict[str, Any]) -> ExtraSnapshot:
    raw_items = payload.get("items_by_task_id", {})
    items_by_task_id: dict[str, TaskExtra] = {}
    if isinstance(raw_items, dict):
        for task_id, extra_payload in raw_items.items():
            if not isinstance(extra_payload, dict):
                continue
            items_by_task_id[str(task_id)] = extra_from_dict(extra_payload)
    return ExtraSnapshot(
        version=max(int(payload.get("version", 2) or 2), 1),
        updated_at_utc=_parse_dt(payload.get("updated_at_utc")) or datetime.now(timezone.utc),
        items_by_task_id=items_by_task_id,
    )


def dumps_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def loads_json(text: str) -> dict[str, Any]:
    payload = json.loads(text or "{}")
    if not isinstance(payload, dict):
        raise ValueError("snapshot payload must be a JSON object")
    return payload

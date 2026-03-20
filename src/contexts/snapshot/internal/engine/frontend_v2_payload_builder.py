from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.contexts.attachments.contracts import attachment_projection_visible
from src.contexts.snapshot.internal.engine.model import Milestone, PrepSnapshot, TaskSheet, TaskView


def _to_str(value: Any) -> str:
    return str(value or "").strip()


def _utc_iso(value: datetime) -> str:
    target = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return target.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_id(prefix: str, raw: str) -> str:
    payload = f"{prefix}:{raw}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def _owner_id(sheet: TaskSheet) -> str:
    raw = _to_str(sheet.owner_id)
    return _stable_id("owner", raw) if raw else "owner:unassigned"


def _group_id(sheet: TaskSheet) -> str:
    raw = _to_str(sheet.group_id)
    return _stable_id("group", raw) if raw else "group:default"


def _stable_payload_hash(payload: dict[str, Any]) -> str:
    base = dict(payload)
    meta = dict(base.get("meta", {}))
    meta["hash"] = ""
    base["meta"] = meta
    serialized = json.dumps(base, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _milestone_sort_key(item: Milestone) -> tuple[str, str, str]:
    planned = item.planned.isoformat() if item.planned else "9999-12-31"
    actual = item.actual.isoformat() if item.actual else "9999-12-31"
    return planned, actual, _to_str(item.type)


def _task_date_range(sheet: TaskSheet) -> tuple[date | None, date | None]:
    dates: list[date] = []
    for key in dict(sheet.timing or {}).keys():
        text = _to_str(key)
        if not text:
            continue
        try:
            dates.append(date.fromisoformat(text[:10]))
        except ValueError:
            continue
    for milestone in list(sheet.milestones or []):
        if milestone.planned is not None:
            dates.append(milestone.planned)
        if milestone.actual is not None:
            dates.append(milestone.actual)
    if not dates:
        return None, None
    ordered = sorted(dates)
    return ordered[0], ordered[-1]


def _window_match(start: date | None, end: date | None, q: FrontendV2Query) -> bool:
    if not q.window_enabled:
        return True
    if q.window_start is None or q.window_end is None:
        return True
    if start is None and end is None:
        return False
    task_start = start or end
    task_end = end or start
    if task_start is None or task_end is None:
        return False
    return task_start <= q.window_end and task_end >= q.window_start


@dataclass(frozen=True)
class FrontendV2Payload:
    """Exact external payload shape: meta + filters + summary + entities + tasks."""

    data: dict[str, Any]


class FrontendV2PayloadBuilder:
    """Build API v2 payload directly from prep snapshot."""

    def build(
        self,
        snap: PrepSnapshot,
        q: Any,
        selected: list[TaskView],
        *,
        env_name: str = "",
        source_sheet_name: str = "",
    ) -> FrontendV2Payload:
        tasks_payload = self.build_tasks(selected)
        entities_payload = self.build_entities(snap, q, selected)
        summary_payload = self.build_summary(tasks_payload)
        summary_payload["peopleTotal"] = len(list(entities_payload.get("people", [])))
        summary_payload["groupsTotal"] = len(list(entities_payload.get("groups", [])))
        payload: dict[str, Any] = {
            "meta": self.build_meta(snap, q, env_name=env_name, source_sheet_name=source_sheet_name),
            "filters": self.build_filters_block(q),
            "summary": summary_payload,
            "entities": entities_payload,
            "tasks": tasks_payload,
        }
        payload["summary"]["tasksTotal"] = self._total_tasks_after_status_designer_filter(snap, q)
        payload["meta"]["hash"] = _stable_payload_hash(payload)
        return FrontendV2Payload(data=payload)

    def build_meta(self, snap: PrepSnapshot, q: Any, *, env_name: str, source_sheet_name: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        return {
            "artifact": "dtm_frontend_api_v2",
            "contractVersion": "2.0.1",
            "generatedAt": _utc_iso(snap.built_at_utc),
            "syncedAt": _utc_iso(now),
            "source": {
                "env": _to_str(env_name),
                "sourceId": snap.source_id,
                "sheetName": _to_str(source_sheet_name),
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
            "paging": {"limit": int(q.limit), "nextCursor": None},
            "sourceHash": snap.raw_source_hash,
            "sourceId": snap.source_id,
            "readmodelSource": "s3_snapshot",
            "queryFilterApplied": True,
            "queryFilterNote": "",
        }

    def build_filters_block(self, q: Any) -> dict[str, Any]:
        return {
            "statuses": list(q.statuses),
            "designer": _to_str(q.designer) or None,
            "limit": int(q.limit),
            "include_people": bool(q.include_people),
            "window": {
                "enabled": bool(q.window_enabled),
                "start": q.window_start.isoformat() if q.window_start else None,
                "end": q.window_end.isoformat() if q.window_end else None,
                "mode": _to_str(q.window_mode) or "intersects",
            },
        }

    def build_entities(self, snap: PrepSnapshot, q: Any, selected: list[TaskView]) -> dict[str, Any]:
        people: list[dict[str, Any]] = []
        if q.include_people:
            seen: set[str] = set()
            for view in selected:
                name = _to_str(view.sheet.owner_id)
                pid = _owner_id(view.sheet)
                if not name or pid in seen:
                    continue
                seen.add(pid)
                people.append(
                    {
                        "id": pid,
                        "name": name,
                        "position": "designer",
                        "links": {"self": f"/api/v2/frontend/entities/people/{pid}"},
                    }
                )
            people.sort(key=lambda item: str(item["id"]))

        groups_map: dict[str, dict[str, Any]] = {}
        milestone_types: dict[str, str] = {}
        for view in selected:
            gid = _group_id(view.sheet)
            if gid not in groups_map:
                groups_map[gid] = {
                    "id": gid,
                    "name": _to_str(view.sheet.group_id) or "Default",
                    "links": {"self": f"/api/v2/frontend/entities/groups/{gid}"},
                }
            for milestone in list(view.sheet.milestones or []):
                key = _to_str(milestone.type)
                if key:
                    milestone_types[key] = key

        return {
            "people": people if q.include_people else [],
            "groups": sorted(groups_map.values(), key=lambda item: str(item["id"])),
            "tags": [],
            "enums": {
                "status": {
                    "work": "In work",
                    "pre_done": "Pre done",
                    "wait": "Waiting",
                    "done": "Done",
                },
                "statusGroups": {"active": ["work", "pre_done"], "final": ["done"]},
                "milestoneType": dict(sorted(milestone_types.items())),
                "milestoneStatus": {
                    "planned": "Planned",
                    "done": "Done",
                    "unknown": "Unknown",
                    "skipped": "Skipped",
                },
            },
        }

    def build_tasks(self, selected: list[TaskView]) -> list[dict[str, Any]]:
        payload: list[dict[str, Any]] = []
        for view in selected:
            sheet = view.sheet
            start, end = _task_date_range(sheet)
            milestones = []
            for milestone in sorted(list(sheet.milestones or []), key=_milestone_sort_key):
                milestones.append(
                    {
                        "type": _to_str(milestone.type),
                        "planned": milestone.planned.isoformat() if milestone.planned else None,
                        "actual": milestone.actual.isoformat() if milestone.actual else None,
                        "status": _to_str(milestone.status) or "planned",
                    }
                )
            payload.append(
                {
                    "id": _to_str(sheet.task_id),
                    "title": _to_str(sheet.title),
                    "brand": _to_str(sheet.brand),
                    "format_": _to_str(sheet.format_),
                    "customer": _to_str(sheet.customer),
                    "history": _to_str(sheet.history),
                    "attachments": [
                        {
                            "id": _to_str(item.attachment_id),
                            "name": _to_str(item.filename_display),
                            "mime": _to_str(item.mime_type),
                            "kind": _to_str(item.kind),
                            "sizeBytes": int(item.size_bytes),
                            "status": _to_str(item.status),
                            "uploadedAt": _utc_iso(item.uploaded_at_utc),
                            "capabilities": list(item.preview_capabilities or []),
                            "meta": {"preview": _to_str(item.preview)} if _to_str(item.preview) else {},
                            "links": {
                                "view": f"/api/task-attachments/{_to_str(item.attachment_id)}/view",
                                "download": f"/api/task-attachments/{_to_str(item.attachment_id)}/download",
                            },
                        }
                        for item in list((view.extra.attachments if view.extra is not None else []) or [])
                        if attachment_projection_visible(item)
                    ],
                    "ownerId": _owner_id(sheet),
                    "groupId": _group_id(sheet),
                    "status": _to_str(sheet.status) or "unknown",
                    "date": {
                        "start": start.isoformat() if start else None,
                        "end": end.isoformat() if end else None,
                        "nextDue": None,
                    },
                    "tags": [],
                    "links": {"self": f"/api/v2/frontend/tasks/{_to_str(sheet.task_id)}"},
                    "milestones": milestones,
                }
            )
        return payload

    def build_summary(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "tasksTotal": len(tasks),
            "tasksReturned": len(tasks),
            "peopleTotal": 0,
            "groupsTotal": 0,
            "milestonesTotal": sum(len(list(item.get("milestones", []))) for item in tasks),
        }

    def select_tasks(self, snap: PrepSnapshot, q: Any) -> list[TaskView]:
        statuses = {str(item).strip().lower() for item in list(q.statuses or []) if str(item).strip()}
        designer_filter = _to_str(q.designer).casefold()
        selected: list[tuple[date | None, date | None, TaskView]] = []
        for view in snap.tasks_by_id.values():
            sheet = view.sheet
            status = _to_str(sheet.status).lower()
            if statuses and status not in statuses:
                continue
            if designer_filter and designer_filter != _to_str(sheet.owner_id).casefold():
                continue
            start, end = _task_date_range(sheet)
            if not _window_match(start, end, q):
                continue
            selected.append((start, end, view))

        def _sort_key(item: tuple[date | None, date | None, TaskView]) -> tuple[str, str, str]:
            start, end, view = item
            end_key = end.isoformat() if end else "0000-00-00"
            start_key = start.isoformat() if start else "0000-00-00"
            return end_key, start_key, _to_str(view.sheet.task_id)

        selected.sort(key=_sort_key, reverse=True)
        limit = max(int(q.limit), 0)
        if limit == 0:
            return []
        return [view for _, _, view in selected[:limit]]

    def _total_tasks_after_status_designer_filter(self, snap: PrepSnapshot, q: Any) -> int:
        statuses = {str(item).strip().lower() for item in list(q.statuses or []) if str(item).strip()}
        designer_filter = _to_str(q.designer).casefold()
        count = 0
        for view in snap.tasks_by_id.values():
            status = _to_str(view.sheet.status).lower()
            if statuses and status not in statuses:
                continue
            if designer_filter and designer_filter != _to_str(view.sheet.owner_id).casefold():
                continue
            count += 1
        return count

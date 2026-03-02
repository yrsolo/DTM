"""Operational repository over normalized YDB tables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.adapters.ydb.client import YdbClient
from src.adapters.ydb.schema import ensure_tables


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


@dataclass(slots=True)
class SyncStateRow:
    source_id: str
    source_hash: str
    synced_at_utc: datetime | None
    last_success_at_utc: datetime | None
    last_error: str | None


class OperationalTaskRepo:
    """YDB repo for dtm_tasks/dtm_task_milestones/dtm_sync_state."""

    def __init__(
        self,
        *,
        endpoint: str,
        database: str,
        tasks_table: str = "dtm_tasks",
        milestones_table: str = "dtm_task_milestones",
        sync_state_table: str = "dtm_sync_state",
        readmodel_table: str = "dtm_readmodel_frontend_v2",
        ensure_schema: bool = False,
    ) -> None:
        self.client = YdbClient(endpoint=endpoint, database=database)
        self.tasks_table = tasks_table
        self.milestones_table = milestones_table
        self.sync_state_table = sync_state_table
        if ensure_schema:
            ensure_tables(
                self.client,
                tasks_table=tasks_table,
                milestones_table=milestones_table,
                sync_state_table=sync_state_table,
                readmodel_table=readmodel_table,
            )

    def upsert_tasks_batch(self, tasks: list[dict[str, Any]]) -> int:
        rows: list[dict[str, Any]] = []
        now = _utc_now()
        for task in tasks:
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                continue
            rows.append(
                {
                    "task_id": task_id,
                    "title": str(task.get("title", task.get("name", ""))).strip(),
                    "brand": str(task.get("brand", "")).strip(),
                    "format_": str(task.get("format_", "")).strip(),
                    "customer": str(task.get("customer", "")).strip(),
                    "raw_timing": str(task.get("raw_timing", "")).strip(),
                    "owner_id": str(task.get("owner_id", task.get("designer", ""))).strip(),
                    "group_id": str(task.get("group_id", task.get("project_name", ""))).strip(),
                    "status": str(task.get("status", task.get("color_status", ""))).strip().lower() or "unknown",
                    "start_date": _to_date(task.get("start_date")),
                    "end_date": _to_date(task.get("end_date")),
                    "next_due_date": _to_date(task.get("next_due_date")),
                    "tags_json": json.dumps(task.get("tags", []), ensure_ascii=False),
                    "links_json": json.dumps(task.get("links", {}), ensure_ascii=False),
                    "task_hash": str(task.get("task_hash", "")).strip() or None,
                    "task_revision": int(task.get("task_revision", 0) or 0),
                    "raw_payload": json.dumps(task.get("raw_payload", task), ensure_ascii=False),
                    "updated_at_utc": now,
                }
            )
        if not rows:
            return 0
        query = f"""
        DECLARE $rows AS List<
            Struct<
                task_id:Utf8,
                title:Utf8,
                brand:Utf8,
                format_:Utf8,
                customer:Utf8,
                raw_timing:Utf8,
                owner_id:Utf8,
                group_id:Utf8,
                status:Utf8,
                start_date:Date?,
                end_date:Date?,
                next_due_date:Date?,
                tags_json:Utf8,
                links_json:Utf8,
                task_hash:Utf8?,
                task_revision:Uint64,
                raw_payload:Utf8,
                updated_at_utc:Timestamp
            >
        >;
        UPSERT INTO `{self.tasks_table}` (
            task_id, title, brand, format_, customer, raw_timing, owner_id, group_id, status, start_date, end_date, next_due_date,
            tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
        )
        SELECT
            task_id, title, brand, format_, customer, raw_timing, owner_id, group_id, status, start_date, end_date, next_due_date,
            tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
        FROM AS_TABLE($rows);
        """
        self.client.execute(query, {"$rows": rows})
        return len(rows)

    def replace_task_milestones(self, task_id: str, milestones: list[dict[str, Any]]) -> int:
        normalized_task_id = str(task_id or "").strip()
        if not normalized_task_id:
            return 0
        delete_query = f"""
        DECLARE $task_id AS Utf8;
        DELETE FROM `{self.milestones_table}` WHERE task_id = $task_id;
        """
        self.client.execute(delete_query, {"$task_id": normalized_task_id})

        rows: list[dict[str, Any]] = []
        for index, milestone in enumerate(milestones):
            rows.append(
                {
                    "task_id": normalized_task_id,
                    "idx": int(milestone.get("idx", index)),
                    "type": str(milestone.get("type", "")).strip() or "unknown",
                    "planned_date": _to_date(milestone.get("planned_date", milestone.get("planned"))),
                    "actual_date": _to_date(milestone.get("actual_date", milestone.get("actual"))),
                    "status": str(milestone.get("status", "unknown")).strip() or "unknown",
                    "raw_text": str(milestone.get("raw_text", "")).strip() or None,
                    "confidence": float(milestone.get("confidence", 0.0) or 0.0),
                    "inference_rule": str(milestone.get("inference_rule", "")).strip() or None,
                }
            )
        if not rows:
            return 0
        query = f"""
        DECLARE $rows AS List<
            Struct<
                task_id:Utf8,
                idx:Uint32,
                type:Utf8,
                planned_date:Date?,
                actual_date:Date?,
                status:Utf8,
                raw_text:Utf8?,
                confidence:Double,
                inference_rule:Utf8?
            >
        >;
        UPSERT INTO `{self.milestones_table}` (
            task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        )
        SELECT
            task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        FROM AS_TABLE($rows);
        """
        self.client.execute(query, {"$rows": rows})
        return len(rows)

    def replace_task_milestones_bulk(self, payload_by_task: dict[str, list[dict[str, Any]]]) -> int:
        """Replace milestones for many tasks with bounded query count."""
        task_ids = [str(task_id).strip() for task_id in payload_by_task.keys() if str(task_id).strip()]
        if not task_ids:
            return 0

        # Full table replace is acceptable because sync reads full source range.
        delete_query = f"DELETE FROM `{self.milestones_table}`;"
        self.client.query(delete_query)

        rows: list[dict[str, Any]] = []
        for task_id, milestones in payload_by_task.items():
            normalized_task_id = str(task_id).strip()
            if not normalized_task_id:
                continue
            for index, milestone in enumerate(milestones):
                rows.append(
                    {
                        "task_id": normalized_task_id,
                        "idx": int(milestone.get("idx", index)),
                        "type": str(milestone.get("type", "")).strip() or "unknown",
                        "planned_date": _to_date(milestone.get("planned_date", milestone.get("planned"))),
                        "actual_date": _to_date(milestone.get("actual_date", milestone.get("actual"))),
                        "status": str(milestone.get("status", "unknown")).strip() or "unknown",
                        "raw_text": str(milestone.get("raw_text", "")).strip() or None,
                        "confidence": float(milestone.get("confidence", 0.0) or 0.0),
                        "inference_rule": str(milestone.get("inference_rule", "")).strip() or None,
                    }
                )

        if not rows:
            return 0

        upsert_query = f"""
        DECLARE $rows AS List<
            Struct<
                task_id:Utf8,
                idx:Uint32,
                type:Utf8,
                planned_date:Date?,
                actual_date:Date?,
                status:Utf8,
                raw_text:Utf8?,
                confidence:Double,
                inference_rule:Utf8?
            >
        >;
        UPSERT INTO `{self.milestones_table}` (
            task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        )
        SELECT
            task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        FROM AS_TABLE($rows);
        """
        self.client.execute(upsert_query, {"$rows": rows})
        return len(rows)

    def get_sync_state(self, source_id: str) -> SyncStateRow | None:
        query = f"""
        DECLARE $source_id AS Utf8;
        SELECT source_id, source_hash, synced_at_utc, last_success_at_utc, last_error
        FROM `{self.sync_state_table}`
        WHERE source_id = $source_id;
        """
        result_sets = self.client.execute(query, {"$source_id": str(source_id).strip()})
        if not result_sets or not result_sets[0].rows:
            return None
        row = result_sets[0].rows[0]
        return SyncStateRow(
            source_id=str(getattr(row, "source_id", "")),
            source_hash=str(getattr(row, "source_hash", "")),
            synced_at_utc=getattr(row, "synced_at_utc", None),
            last_success_at_utc=getattr(row, "last_success_at_utc", None),
            last_error=str(getattr(row, "last_error", "")).strip() or None,
        )

    def set_sync_state(self, source_id: str, source_hash: str, *, last_error: str | None = None) -> None:
        query = f"""
        DECLARE $source_id AS Utf8;
        DECLARE $source_hash AS Utf8;
        DECLARE $synced_at_utc AS Timestamp;
        DECLARE $last_success_at_utc AS Timestamp;
        DECLARE $last_error AS Utf8?;
        UPSERT INTO `{self.sync_state_table}` (
            source_id, source_hash, synced_at_utc, last_success_at_utc, last_error
        )
        VALUES ($source_id, $source_hash, $synced_at_utc, $last_success_at_utc, $last_error);
        """
        now = _utc_now()
        self.client.execute(
            query,
            {
                "$source_id": str(source_id).strip(),
                "$source_hash": str(source_hash).strip(),
                "$synced_at_utc": now,
                "$last_success_at_utc": now,
                "$last_error": str(last_error).strip() if last_error else None,
            },
        )

    def list_tasks(self, *, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        status_filter = [str(item).strip().lower() for item in (statuses or []) if str(item).strip()]
        query = f"""
        DECLARE $statuses AS List<Utf8>;
        SELECT
            task_id, title, brand, format_, customer, raw_timing, owner_id, group_id, status, start_date, end_date, next_due_date,
            tags_json, links_json, task_hash, task_revision, updated_at_utc
        FROM `{self.tasks_table}`
        WHERE
            ListLength($statuses) = 0
            OR status IN $statuses;
        """
        result_sets = self.client.execute(query, {"$statuses": status_filter})
        if not result_sets:
            return []
        rows: list[dict[str, Any]] = []
        for row in result_sets[0].rows:
            rows.append(
                {
                    "task_id": str(getattr(row, "task_id", "")),
                    "title": str(getattr(row, "title", "")),
                    "brand": str(getattr(row, "brand", "")),
                    "format_": str(getattr(row, "format_", "")),
                    "customer": str(getattr(row, "customer", "")),
                    "raw_timing": str(getattr(row, "raw_timing", "")),
                    "owner_id": str(getattr(row, "owner_id", "")),
                    "group_id": str(getattr(row, "group_id", "")),
                    "status": str(getattr(row, "status", "")),
                    "start_date": getattr(row, "start_date", None),
                    "end_date": getattr(row, "end_date", None),
                    "next_due_date": getattr(row, "next_due_date", None),
                    "tags_json": str(getattr(row, "tags_json", "[]")),
                    "links_json": str(getattr(row, "links_json", "{}")),
                    "task_hash": str(getattr(row, "task_hash", "")) or None,
                    "task_revision": int(getattr(row, "task_revision", 0) or 0),
                    "updated_at_utc": getattr(row, "updated_at_utc", None),
                }
            )
        return rows

    def list_milestones(self, *, task_ids: list[str] | None = None) -> list[dict[str, Any]]:
        keys = [str(task_id).strip() for task_id in (task_ids or []) if str(task_id).strip()]
        query = f"""
        DECLARE $task_ids AS List<Utf8>;
        SELECT task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        FROM `{self.milestones_table}`
        WHERE
            ListLength($task_ids) = 0
            OR task_id IN $task_ids;
        """
        result_sets = self.client.execute(query, {"$task_ids": keys})
        if not result_sets:
            return []
        rows: list[dict[str, Any]] = []
        for row in result_sets[0].rows:
            rows.append(
                {
                    "task_id": str(getattr(row, "task_id", "")),
                    "idx": int(getattr(row, "idx", 0) or 0),
                    "type": str(getattr(row, "type", "")),
                    "planned_date": getattr(row, "planned_date", None),
                    "actual_date": getattr(row, "actual_date", None),
                    "status": str(getattr(row, "status", "")) or "unknown",
                    "raw_text": str(getattr(row, "raw_text", "")) or None,
                    "confidence": float(getattr(row, "confidence", 0.0) or 0.0),
                    "inference_rule": str(getattr(row, "inference_rule", "")) or None,
                }
            )
        return rows

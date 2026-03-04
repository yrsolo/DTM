"""Operational repository over normalized YDB tables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
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
    if isinstance(value, (int, float)):
        raw = int(value)
        if raw <= 0:
            return None
        # YDB Date can be returned as days since Unix epoch.
        if raw < 100_000:
            return date(1970, 1, 1) + timedelta(days=raw)
        # Fallback for epoch-like timestamps.
        if raw > 10_000_000_000:
            raw //= 1_000
        return datetime.fromtimestamp(raw, tz=timezone.utc).date()
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
    preflight_hash_50: str
    source_hash_full: str
    synced_at_utc: datetime | None
    last_full_sync_at_utc: datetime | None
    last_success_at_utc: datetime | None
    last_error: str | None
    last_error_code: str | None
    last_error_at_utc: datetime | None

    @property
    def source_hash(self) -> str:
        return self.source_hash_full


class OperationalTaskRepo:
    """YDB repo for dtm_tasks/dtm_task_milestones/dtm_sync_state."""

    def __init__(
        self,
        *,
        endpoint: str,
        database: str,
        sa_json_credentials: str | None = None,
        sa_key_file: str | None = None,
        tasks_table: str = "dtm_tasks",
        milestones_table: str = "dtm_task_milestones",
        milestones_versions_table: str = "dtm_task_milestones_v",
        versions_table: str = "dtm_task_versions",
        sync_state_table: str = "dtm_sync_state",
        readmodel_table: str = "dtm_readmodel_frontend_v2",
        ensure_schema: bool = False,
    ) -> None:
        self.client = YdbClient(
            endpoint=endpoint,
            database=database,
            sa_json_credentials=sa_json_credentials,
            sa_key_file=sa_key_file,
        )
        self.tasks_table = tasks_table
        self.milestones_table = milestones_table
        self.milestones_versions_table = milestones_versions_table
        self.versions_table = versions_table
        self.sync_state_table = sync_state_table
        if ensure_schema:
            ensure_tables(
                self.client,
                tasks_table=tasks_table,
                milestones_table=milestones_table,
                milestones_versioned_table=milestones_versions_table,
                versions_table=versions_table,
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
        try:
            self.client.execute(query, {"$rows": rows})
        except Exception as exc:
            if not self._is_missing_task_columns_error(exc):
                raise
            legacy_rows = [
                {
                    "task_id": item["task_id"],
                    "title": item["title"],
                    "owner_id": item["owner_id"],
                    "group_id": item["group_id"],
                    "status": item["status"],
                    "start_date": item["start_date"],
                    "end_date": item["end_date"],
                    "next_due_date": item["next_due_date"],
                    "tags_json": item["tags_json"],
                    "links_json": item["links_json"],
                    "task_hash": item["task_hash"],
                    "task_revision": item["task_revision"],
                    "raw_payload": item["raw_payload"],
                    "updated_at_utc": item["updated_at_utc"],
                }
                for item in rows
            ]
            legacy_query = f"""
            DECLARE $rows AS List<
                Struct<
                    task_id:Utf8,
                    title:Utf8,
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
                task_id, title, owner_id, group_id, status, start_date, end_date, next_due_date,
                tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
            )
            SELECT
                task_id, title, owner_id, group_id, status, start_date, end_date, next_due_date,
                tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
            FROM AS_TABLE($rows);
            """
            self.client.execute(legacy_query, {"$rows": legacy_rows})
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

        # Safe replace: delete only affected task_ids, never full-table wipe.
        delete_query = f"""
        DECLARE $task_ids AS List<Utf8>;
        DELETE FROM `{self.milestones_table}`
        WHERE task_id IN $task_ids;
        """
        chunk_size = 200
        for index in range(0, len(task_ids), chunk_size):
            chunk = task_ids[index : index + chunk_size]
            self.client.execute(delete_query, {"$task_ids": chunk})

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

    def upsert_task_milestones_versions_bulk(
        self,
        payload_by_task_version: dict[tuple[str, int], list[dict[str, Any]]],
    ) -> int:
        """Upsert versioned milestones rows keyed by (task_id, version, idx)."""
        if not payload_by_task_version:
            return 0

        rows: list[dict[str, Any]] = []
        for (task_id, version), milestones in payload_by_task_version.items():
            normalized_task_id = str(task_id).strip()
            normalized_version = int(version or 0)
            if not normalized_task_id or normalized_version <= 0:
                continue
            for index, milestone in enumerate(milestones):
                rows.append(
                    {
                        "task_id": normalized_task_id,
                        "version": normalized_version,
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
                version:Uint64,
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
        UPSERT INTO `{self.milestones_versions_table}` (
            task_id, version, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        )
        SELECT
            task_id, version, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
        FROM AS_TABLE($rows);
        """
        self.client.execute(upsert_query, {"$rows": rows})
        return len(rows)

    def get_sync_state(self, source_id: str) -> SyncStateRow | None:
        query = f"""
        DECLARE $source_id AS Utf8;
        SELECT
            source_id, preflight_hash_50, source_hash_full, synced_at_utc, last_full_sync_at,
            last_success_at_utc, last_error, last_error_code, last_error_at_utc
        FROM `{self.sync_state_table}`
        WHERE source_id = $source_id;
        """
        try:
            result_sets = self.client.execute(query, {"$source_id": str(source_id).strip()})
            legacy = False
        except Exception as exc:
            text = str(exc).lower()
            if "member not found" not in text:
                raise
            legacy = True
            legacy_query = f"""
            DECLARE $source_id AS Utf8;
            SELECT source_id, source_hash, synced_at_utc, last_success_at_utc, last_error
            FROM `{self.sync_state_table}`
            WHERE source_id = $source_id;
            """
            result_sets = self.client.execute(legacy_query, {"$source_id": str(source_id).strip()})
        if not result_sets or not result_sets[0].rows:
            return None
        row = result_sets[0].rows[0]
        if legacy:
            source_hash = str(getattr(row, "source_hash", ""))
            return SyncStateRow(
                source_id=str(getattr(row, "source_id", "")),
                preflight_hash_50=source_hash,
                source_hash_full=source_hash,
                synced_at_utc=getattr(row, "synced_at_utc", None),
                last_full_sync_at_utc=getattr(row, "synced_at_utc", None),
                last_success_at_utc=getattr(row, "last_success_at_utc", None),
                last_error=str(getattr(row, "last_error", "")).strip() or None,
                last_error_code=None,
                last_error_at_utc=None,
            )
        return SyncStateRow(
            source_id=str(getattr(row, "source_id", "")),
            preflight_hash_50=str(getattr(row, "preflight_hash_50", "")),
            source_hash_full=str(getattr(row, "source_hash_full", "")),
            synced_at_utc=getattr(row, "synced_at_utc", None),
            last_full_sync_at_utc=getattr(row, "last_full_sync_at", None),
            last_success_at_utc=getattr(row, "last_success_at_utc", None),
            last_error=str(getattr(row, "last_error", "")).strip() or None,
            last_error_code=str(getattr(row, "last_error_code", "")).strip() or None,
            last_error_at_utc=getattr(row, "last_error_at_utc", None),
        )

    def set_sync_state(
        self,
        *,
        source_id: str,
        preflight_hash_50: str,
        source_hash_full: str,
        synced_at_utc: datetime | None = None,
        last_full_sync_at_utc: datetime | None = None,
        last_success_at_utc: datetime | None = None,
        last_error: str | None = None,
        last_error_code: str | None = None,
        last_error_at_utc: datetime | None = None,
    ) -> None:
        query = f"""
        DECLARE $source_id AS Utf8;
        DECLARE $preflight_hash_50 AS Utf8;
        DECLARE $source_hash_full AS Utf8;
        DECLARE $synced_at_utc AS Timestamp;
        DECLARE $last_full_sync_at AS Timestamp?;
        DECLARE $last_success_at_utc AS Timestamp;
        DECLARE $last_error AS Utf8?;
        DECLARE $last_error_code AS Utf8?;
        DECLARE $last_error_at_utc AS Timestamp?;
        UPSERT INTO `{self.sync_state_table}` (
            source_id, preflight_hash_50, source_hash_full, synced_at_utc, last_full_sync_at,
            last_success_at_utc, last_error, last_error_code, last_error_at_utc
        )
        VALUES (
            $source_id, $preflight_hash_50, $source_hash_full, $synced_at_utc, $last_full_sync_at,
            $last_success_at_utc, $last_error, $last_error_code, $last_error_at_utc
        );
        """
        now = synced_at_utc or _utc_now()
        try:
            self.client.execute(
                query,
                {
                    "$source_id": str(source_id).strip(),
                    "$preflight_hash_50": str(preflight_hash_50).strip(),
                    "$source_hash_full": str(source_hash_full).strip(),
                    "$synced_at_utc": now,
                    "$last_full_sync_at": last_full_sync_at_utc,
                    "$last_success_at_utc": last_success_at_utc or now,
                    "$last_error": str(last_error).strip() if last_error else None,
                    "$last_error_code": str(last_error_code).strip() if last_error_code else None,
                    "$last_error_at_utc": last_error_at_utc,
                },
            )
        except Exception as exc:
            text = str(exc).lower()
            if "member not found" not in text:
                raise
            legacy_query = f"""
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
            self.client.execute(
                legacy_query,
                {
                    "$source_id": str(source_id).strip(),
                    "$source_hash": str(source_hash_full).strip(),
                    "$synced_at_utc": now,
                    "$last_success_at_utc": last_success_at_utc or now,
                    "$last_error": str(last_error).strip() if last_error else None,
                },
            )

    def upsert_task_version(
        self,
        *,
        task_id: str,
        version: int,
        status: str,
        content_hash: str,
        payload_json: str,
        created_at_utc: datetime | None = None,
    ) -> None:
        query = f"""
        DECLARE $task_id AS Utf8;
        DECLARE $version AS Uint64;
        DECLARE $status AS Utf8;
        DECLARE $content_hash AS Utf8;
        DECLARE $payload_json AS Utf8;
        DECLARE $created_at_utc AS Timestamp;
        UPSERT INTO `{self.versions_table}` (
            task_id, version, status, content_hash, payload_json, created_at_utc
        )
        VALUES (
            $task_id, $version, $status, $content_hash, $payload_json, $created_at_utc
        );
        """
        try:
            self.client.execute(
                query,
                {
                    "$task_id": str(task_id).strip(),
                    "$version": int(version),
                    "$status": str(status).strip() or "active",
                    "$content_hash": str(content_hash).strip(),
                    "$payload_json": payload_json,
                    "$created_at_utc": created_at_utc or _utc_now(),
                },
            )
        except Exception as exc:
            text = str(exc).lower()
            if "path not found" in text or "table not found" in text:
                return
            raise

    def archive_task_version(self, *, task_id: str, version: int) -> None:
        query = f"""
        DECLARE $task_id AS Utf8;
        DECLARE $version AS Uint64;
        UPDATE `{self.versions_table}`
        SET status = "archive"
        WHERE task_id = $task_id AND version = $version;
        """
        try:
            self.client.execute(
                query,
                {
                    "$task_id": str(task_id).strip(),
                    "$version": int(version),
                },
            )
        except Exception as exc:
            text = str(exc).lower()
            if "path not found" in text or "table not found" in text:
                return
            raise

    def list_tasks(self, *, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        status_filter = [str(item).strip().lower() for item in (statuses or []) if str(item).strip()]
        query = f"""
        DECLARE $statuses AS List<Utf8>;
        SELECT
            task_id, title, brand, format_, customer, raw_timing, owner_id, group_id, status, start_date, end_date, next_due_date,
            tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
        FROM `{self.tasks_table}`
        WHERE
            ListLength($statuses) = 0
            OR status IN $statuses;
        """
        try:
            result_sets = self.client.execute(query, {"$statuses": status_filter})
            missing_extended_columns = False
        except Exception as exc:
            if not self._is_missing_task_columns_error(exc):
                raise
            missing_extended_columns = True
            legacy_query = f"""
            DECLARE $statuses AS List<Utf8>;
            SELECT
                task_id, title, owner_id, group_id, status, start_date, end_date, next_due_date,
                tags_json, links_json, task_hash, task_revision, raw_payload, updated_at_utc
            FROM `{self.tasks_table}`
            WHERE
                ListLength($statuses) = 0
                OR status IN $statuses;
            """
            result_sets = self.client.execute(legacy_query, {"$statuses": status_filter})
        if not result_sets:
            return []
        rows: list[dict[str, Any]] = []
        for row in result_sets[0].rows:
            rows.append(
                {
                    "task_id": str(getattr(row, "task_id", "")),
                    "title": str(getattr(row, "title", "")),
                    "brand": "" if missing_extended_columns else str(getattr(row, "brand", "")),
                    "format_": "" if missing_extended_columns else str(getattr(row, "format_", "")),
                    "customer": "" if missing_extended_columns else str(getattr(row, "customer", "")),
                    "raw_timing": "" if missing_extended_columns else str(getattr(row, "raw_timing", "")),
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
                    "current_version": int(getattr(row, "task_revision", 0) or 0),
                    "updated_at_utc": getattr(row, "updated_at_utc", None),
                    "raw_payload": str(getattr(row, "raw_payload", "{}")),
                }
            )
        return rows

    @staticmethod
    def _is_missing_task_columns_error(exc: Exception) -> bool:
        text = str(exc).lower()
        if "member not found" not in text:
            return False
        return any(
            marker in text
            for marker in ("brand", "format_", "customer", "raw_timing", "raw_payload")
        )

    def list_milestones(
        self,
        *,
        task_ids: list[str] | None = None,
        include_details: bool = True,
    ) -> list[dict[str, Any]]:
        keys = [str(task_id).strip() for task_id in (task_ids or []) if str(task_id).strip()]
        if include_details:
            query = f"""
            DECLARE $task_ids AS List<Utf8>;
            SELECT task_id, idx, type, planned_date, actual_date, status, raw_text, confidence, inference_rule
            FROM `{self.milestones_table}`
            WHERE
                ListLength($task_ids) = 0
                OR task_id IN $task_ids;
            """
        else:
            query = f"""
            DECLARE $task_ids AS List<Utf8>;
            SELECT task_id, idx, type, planned_date
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
                    "actual_date": getattr(row, "actual_date", None) if include_details else None,
                    "status": (str(getattr(row, "status", "")) or "unknown") if include_details else "unknown",
                    "raw_text": (str(getattr(row, "raw_text", "")) or None) if include_details else None,
                    "confidence": float(getattr(row, "confidence", 0.0) or 0.0) if include_details else 0.0,
                    "inference_rule": (str(getattr(row, "inference_rule", "")) or None) if include_details else None,
                }
            )
        return rows

    def list_milestones_for_versions(
        self,
        *,
        task_versions: dict[str, int],
        include_details: bool = True,
    ) -> list[dict[str, Any]]:
        keys = [
            {"task_id": str(task_id).strip(), "version": int(version)}
            for task_id, version in (task_versions or {}).items()
            if str(task_id).strip() and int(version or 0) > 0
        ]
        if not keys:
            return []

        if include_details:
            query = f"""
            DECLARE $keys AS List<Struct<task_id:Utf8, version:Uint64>>;
            SELECT
                m.task_id AS task_id,
                m.version AS version,
                m.idx AS idx,
                m.type AS type,
                m.planned_date AS planned_date,
                m.actual_date AS actual_date,
                m.status AS status,
                m.raw_text AS raw_text,
                m.confidence AS confidence,
                m.inference_rule AS inference_rule
            FROM `{self.milestones_versions_table}` AS m
            INNER JOIN AS_TABLE($keys) AS k
            ON m.task_id = k.task_id AND m.version = k.version;
            """
        else:
            query = f"""
            DECLARE $keys AS List<Struct<task_id:Utf8, version:Uint64>>;
            SELECT
                m.task_id AS task_id,
                m.version AS version,
                m.idx AS idx,
                m.type AS type,
                m.planned_date AS planned_date
            FROM `{self.milestones_versions_table}` AS m
            INNER JOIN AS_TABLE($keys) AS k
            ON m.task_id = k.task_id AND m.version = k.version;
            """
        try:
            result_sets = self.client.execute(query, {"$keys": keys})
        except Exception as exc:
            text = str(exc).lower()
            if "path not found" in text or "table not found" in text:
                return []
            raise
        if not result_sets:
            return []

        rows: list[dict[str, Any]] = []
        for row in result_sets[0].rows:
            rows.append(
                {
                    "task_id": str(getattr(row, "task_id", "")),
                    "version": int(getattr(row, "version", 0) or 0),
                    "idx": int(getattr(row, "idx", 0) or 0),
                    "type": str(getattr(row, "type", "")),
                    "planned_date": getattr(row, "planned_date", None),
                    "actual_date": getattr(row, "actual_date", None) if include_details else None,
                    "status": (str(getattr(row, "status", "")) or "unknown") if include_details else "unknown",
                    "raw_text": (str(getattr(row, "raw_text", "")) or None) if include_details else None,
                    "confidence": float(getattr(row, "confidence", 0.0) or 0.0) if include_details else 0.0,
                    "inference_rule": (str(getattr(row, "inference_rule", "")) or None) if include_details else None,
                }
            )
        return rows

"""Build and persist frontend v2 readmodel snapshot from operational tables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

from core.api_payload_v2 import build_frontend_api_payload_v2
from core.models.people import Person
from src.adapters.ydb.operational_repo import OperationalTaskRepo
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo


def _utc_iso(value: datetime | None = None) -> str:
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 1e18:
            raw = raw / 1_000_000_000.0
        elif raw > 1e15:
            raw = raw / 1_000_000.0
        elif raw > 1e12:
            raw = raw / 1_000.0
        now = datetime.fromtimestamp(raw, tz=timezone.utc)
    elif isinstance(value, datetime):
        now = value
    else:
        now = datetime.now(timezone.utc)
    return now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class _TaskView:
    id: str
    name: str
    designer: str
    status: str
    color_status: str
    history: str
    brand: str
    format_: str
    project_name: str
    customer: str
    raw_timing: str
    timing: dict[Any, list[str]]


@dataclass(slots=True)
class ReadmodelBuildResult:
    readmodel_id: str
    source_hash: str
    changed: bool
    tasks_count: int
    ydb_queries_count: int


class FrontendReadmodelBuilderService:
    """Build `frontend_v2:default` payload and persist it in YDB."""

    def __init__(
        self,
        *,
        operational_repo: OperationalTaskRepo,
        readmodel_repo: FrontendReadmodelRepo,
        source_id: str,
        env_name: str,
        source_sheet_name: str,
    ) -> None:
        self.operational_repo = operational_repo
        self.readmodel_repo = readmodel_repo
        self.source_id = source_id
        self.env_name = env_name
        self.source_sheet_name = source_sheet_name

    def run(
        self,
        *,
        readmodel_id: str = "frontend_v2:default",
        force_rebuild: bool = False,
    ) -> ReadmodelBuildResult:
        sync_state = self.operational_repo.get_sync_state(self.source_id)
        source_hash = sync_state.source_hash if sync_state is not None else ""
        if not source_hash:
            return ReadmodelBuildResult(
                readmodel_id=readmodel_id,
                source_hash="",
                changed=False,
                tasks_count=0,
                ydb_queries_count=self.operational_repo.client.stats.ydb_queries_count,
            )
        existing = self.readmodel_repo.get_readmodel(readmodel_id)
        if (not force_rebuild) and existing is not None and existing.built_from_source_hash == source_hash:
            payload = existing.payload()
            tasks_count = len(payload.get("tasks", [])) if isinstance(payload, dict) else 0
            return ReadmodelBuildResult(
                readmodel_id=readmodel_id,
                source_hash=source_hash,
                changed=False,
                tasks_count=tasks_count,
                ydb_queries_count=self.operational_repo.client.stats.ydb_queries_count + self.readmodel_repo.client.stats.ydb_queries_count,
            )

        task_rows = self.operational_repo.list_tasks(statuses=["work", "pre_done"])
        people_views = self._build_people_from_task_rows(task_rows)
        task_versions: dict[str, int] = {}
        for row in task_rows:
            task_id = str(row.get("task_id", "")).strip()
            current_version = int(row.get("current_version", row.get("task_revision", 0)) or 0)
            if task_id and current_version > 0:
                task_versions[task_id] = current_version

        milestone_rows = self.operational_repo.list_milestones_for_versions(task_versions=task_versions)
        milestones_by_task: dict[str, list[dict[str, Any]]] = {}
        for item in milestone_rows:
            task_id = str(item.get("task_id", "")).strip()
            if not task_id:
                continue
            row_version = int(item.get("version", 0) or 0)
            expected_version = int(task_versions.get(task_id, 0) or 0)
            if expected_version > 0 and row_version > 0 and row_version != expected_version:
                continue
            milestones_by_task.setdefault(task_id, []).append(item)
        for rows in milestones_by_task.values():
            rows.sort(key=lambda row: int(row.get("idx", 0)))

        task_views: list[_TaskView] = []
        synthetic_start_count = 0
        synthetic_examples: list[str] = []
        for row in task_rows:
            task_id = str(row.get("task_id", "")).strip()
            if not task_id:
                continue
            timing: dict[Any, list[str]] = {}
            for milestone in milestones_by_task.get(task_id, []):
                planned_iso = self._coerce_date_iso(milestone.get("planned_date"))
                if not planned_iso:
                    continue
                timing.setdefault(planned_iso, []).append(str(milestone.get("type", "unknown")))
            if not timing:
                synthetic_start_count += 1
                if len(synthetic_examples) < 10:
                    synthetic_examples.append(f"{task_id}:{task_versions.get(task_id, 0)}")
                planned = self._resolve_synthetic_start_date(row)
                timing.setdefault(planned, []).append("start")
            task_views.append(
                _TaskView(
                    id=task_id,
                    name=str(row.get("title", "")).strip(),
                    designer=str(row.get("owner_id", "")).strip(),
                    status=str(row.get("status", "")).strip(),
                    color_status=str(row.get("status", "")).strip(),
                    history=self._extract_history(row),
                    brand=str(row.get("brand", "")).strip(),
                    format_=str(row.get("format_", "")).strip(),
                    project_name=str(row.get("group_id", "")).strip(),
                    customer=str(row.get("customer", "")).strip(),
                    raw_timing=str(row.get("raw_timing", "")).strip(),
                    timing=timing,
                )
            )

        payload = build_frontend_api_payload_v2(
            tasks=task_views,
            people=people_views,
            env_name=self.env_name,
            source_sheet_name=self.source_sheet_name,
            statuses=["work", "pre_done"],
            limit=500,
            include_people=True,
            designer_filter="",
        )
        payload["meta"]["syncedAt"] = _utc_iso(sync_state.last_success_at_utc if sync_state else None)
        payload["meta"]["source"]["sourceId"] = self.source_id
        payload["meta"]["source"]["sheetName"] = self.source_sheet_name
        payload["meta"]["source"]["sheetUrl"] = None
        payload["meta"]["features"]["readmodelStored"] = True
        payload["meta"]["features"]["apiReadmodelOnly"] = True
        if synthetic_start_count > 0:
            warnings = payload["meta"].setdefault("warnings", [])
            if "synthetic_start_used" not in warnings:
                warnings.append("synthetic_start_used")
            print(f"milestones_synthetic_start_count={synthetic_start_count} samples={','.join(synthetic_examples)}")

        row = self.readmodel_repo.upsert_readmodel(
            payload,
            readmodel_id=readmodel_id,
            contract_version=str(payload.get("meta", {}).get("contractVersion", "2.0.1")),
            built_from_source_hash=source_hash,
        )
        parsed_payload = json.loads(row.payload_json)
        return ReadmodelBuildResult(
            readmodel_id=row.readmodel_id,
            source_hash=source_hash,
            changed=True,
            tasks_count=len(parsed_payload.get("tasks", [])) if isinstance(parsed_payload, dict) else 0,
            ydb_queries_count=self.operational_repo.client.stats.ydb_queries_count + self.readmodel_repo.client.stats.ydb_queries_count,
        )

    @staticmethod
    def _extract_history(row: dict[str, Any]) -> str:
        raw_payload = row.get("raw_payload")
        payload_obj: dict[str, Any] = {}
        if isinstance(raw_payload, dict):
            payload_obj = raw_payload
        elif isinstance(raw_payload, str):
            text = raw_payload.strip()
            if text:
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        payload_obj = parsed
                except json.JSONDecodeError:
                    payload_obj = {}
        history = str(payload_obj.get("history", "")).strip()
        if history:
            return history
        legacy_status = str(payload_obj.get("status", "")).strip()
        if legacy_status:
            return legacy_status
        return str(row.get("status", "")).strip()

    @staticmethod
    def _resolve_synthetic_start_date(row: dict[str, Any]) -> str:
        for key in ("created_at_utc", "first_seen_at_utc", "updated_at_utc", "next_due_date", "start_date", "end_date"):
            value = row.get(key)
            normalized = FrontendReadmodelBuilderService._coerce_date_iso(value)
            if normalized:
                return normalized
        return datetime.now(timezone.utc).date().isoformat()

    @staticmethod
    def _coerce_date_iso(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, (int, float)):
            # YDB Date is often represented as days since Unix epoch.
            return (date(1970, 1, 1) + timedelta(days=int(value))).isoformat()
        text = str(value).strip()
        if not text:
            return None
        if text.isdigit():
            return (date(1970, 1, 1) + timedelta(days=int(text))).isoformat()
        if len(text) >= 10:
            candidate = text[:10]
            try:
                date.fromisoformat(candidate)
                return candidate
            except ValueError:
                return None
        return None

    @staticmethod
    def _build_people_from_task_rows(rows: list[dict[str, Any]]) -> list[Person]:
        people_by_id: dict[str, Person] = {}
        for row in rows:
            owner_id = str(row.get("owner_id", "")).strip()
            if not owner_id:
                continue
            raw_payload = row.get("raw_payload")
            designer_name = ""
            payload_obj: dict[str, Any] = {}
            if isinstance(raw_payload, dict):
                payload_obj = raw_payload
            elif isinstance(raw_payload, str):
                text = raw_payload.strip()
                if text:
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict):
                            payload_obj = parsed
                    except json.JSONDecodeError:
                        payload_obj = {}
            if payload_obj:
                designer_name = str(payload_obj.get("designer", "")).strip()
            person = Person(
                person_id=owner_id,
                name=designer_name or owner_id,
                email="",
                position="designer",
                telegram_id="",
                chat_id="",
                info="",
                vacation="",
            )
            people_by_id[owner_id] = person
        return sorted(people_by_id.values(), key=lambda item: item.id)

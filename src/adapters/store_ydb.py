"""Operational store adapters.

YDB (serverless, gRPC SDK) is the primary migration target.
JSON-backed adapter remains for local tests/mocks only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import pandas as pd


class OperationalStore(Protocol):
    """Store contract for normalized task upserts."""

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]: ...
    def list_tasks(self) -> list[dict[str, Any]]: ...


class _StoreTimingDiagnostics:
    """Compatibility shim for planner quality report counters."""

    def __init__(self) -> None:
        self.parse_issues: list[str] = []
        self.total_parse_errors: int = 0


class StoreTaskView:
    """Task-like projection over operational store records."""

    def __init__(
        self,
        task_id: str,
        name: str,
        designer: str,
        status: str,
        color_status: str,
        brand: str,
        format_: str,
        project_name: str,
        customer: str,
        raw_timing: str,
        timing: dict[pd.Timestamp, list[str]],
    ) -> None:
        self.id = task_id
        self.name = name
        self.designer = designer
        self.status = status
        self.color_status = color_status
        self.brand = brand
        self.format_ = format_
        self.project_name = project_name
        self.customer = customer
        self.raw_timing = raw_timing
        self.timing = timing

    @property
    def min_date(self) -> pd.Timestamp | None:
        return min(self.timing.keys()) if self.timing else None

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None


def parse_store_timing(rows: Any) -> dict[pd.Timestamp, list[str]]:
    """Parse serialized timing list from operational store record."""
    if not isinstance(rows, list):
        return {}
    parsed: dict[pd.Timestamp, list[str]] = {}
    for item in rows:
        if not isinstance(item, dict):
            continue
        date_text = str(item.get("date", "")).strip()
        if not date_text:
            continue
        try:
            date_value = pd.Timestamp(date_text)
        except Exception:
            continue
        stages = item.get("stages", [])
        if not isinstance(stages, list):
            stages = [str(stages)]
        parsed[date_value] = [str(stage) for stage in stages]
    return parsed


def store_records_to_tasks(records: list[dict[str, Any]]) -> list[StoreTaskView]:
    """Convert operational store payloads into task-like rows."""
    tasks: list[StoreTaskView] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        task_id = str(record.get("task_id", "")).strip()
        if not task_id:
            continue
        color_status = str(record.get("color_status", record.get("status", ""))).strip().lower() or "work"
        tasks.append(
            StoreTaskView(
                task_id=task_id,
                name=str(record.get("name", "")).strip(),
                designer=str(record.get("designer", "")).strip(),
                status=str(record.get("status", "")).strip(),
                color_status=color_status,
                brand=str(record.get("brand", "")).strip(),
                format_=str(record.get("format_", "")).strip(),
                project_name=str(record.get("project_name", "")).strip(),
                customer=str(record.get("customer", "")).strip(),
                raw_timing=str(record.get("raw_timing", "")).strip(),
                timing=parse_store_timing(record.get("timing")),
            )
        )
    return tasks


class StoreTaskRepository:
    """Read-only task repository over OperationalStore."""

    def __init__(self, store: OperationalStore) -> None:
        self.store = store
        self.row_issues: list[str] = []
        self.timing_parser = _StoreTimingDiagnostics()

    def get_all_tasks(self) -> list[StoreTaskView]:
        return store_records_to_tasks(self.store.list_tasks())

    def get_task_by_color_status(self, color_status: Any) -> list[StoreTaskView]:
        values = color_status if isinstance(color_status, (list, tuple, set)) else [color_status]
        target = {str(item).strip().lower() for item in values if str(item).strip()}
        tasks = self.get_all_tasks()
        if not target:
            return tasks
        return [task for task in tasks if str(task.color_status).strip().lower() in target]

    def get_tasks_by_date(self, date: pd.Timestamp) -> list[StoreTaskView]:
        tasks = self.get_task_by_color_status(["work"])
        return [task for task in tasks if date in task.timing]


class JsonOperationalStore:
    """Minimal JSON-backed upsert store for normalized records."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"tasks": {}}
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Upsert tasks by `task_id` and return updated payload."""
        store = self.load()
        tasks_map = store.setdefault("tasks", {})
        for task in tasks:
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                continue
            tasks_map[task_id] = task
        self.save(store)
        return store

    def list_tasks(self) -> list[dict[str, Any]]:
        store = self.load()
        tasks_map = store.get("tasks", {})
        if not isinstance(tasks_map, dict):
            return []
        rows: list[dict[str, Any]] = []
        for task_id, payload in tasks_map.items():
            if not isinstance(payload, dict):
                continue
            row = dict(payload)
            row.setdefault("task_id", str(task_id))
            rows.append(row)
        return rows


class YdbOperationalStore:
    """YDB-backed operational store.

    Table schema (created lazily):
    - task_id Utf8 (PK)
    - payload Utf8
    """

    def __init__(self, endpoint: str, database: str, table_path: str = "dtm_operational_tasks") -> None:
        if not endpoint.strip() or not database.strip():
            raise ValueError("YDB endpoint/database are required for YdbOperationalStore")
        self.endpoint = endpoint
        self.database = database
        self.table_path = table_path
        self._driver = None
        self._session_pool = None

    def _ensure_client(self) -> None:
        if self._session_pool is not None:
            return
        try:
            import ydb
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("ydb package is required for YdbOperationalStore") from exc

        driver = ydb.Driver(
            endpoint=self.endpoint,
            database=self.database,
            credentials=ydb.credentials_from_env_variables(),
        )
        driver.wait(fail_fast=True, timeout=5)
        self._driver = driver
        self._session_pool = ydb.SessionPool(driver)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        query = f"""
        CREATE TABLE `{self.table_path}` (
            task_id Utf8,
            payload Utf8,
            PRIMARY KEY (task_id)
        );
        """

        def _create(session) -> None:
            try:
                session.execute_scheme(query)
            except Exception as exc:
                text = str(exc).lower()
                # Table may already exist; keep idempotent.
                if "exists" in text or "already" in text:
                    return
                raise

        self._session_pool.retry_operation_sync(_create)

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        self._ensure_client()
        inserted = 0

        def _upsert(session) -> None:
            nonlocal inserted
            for task in tasks:
                task_id = str(task.get("task_id", "")).strip()
                if not task_id:
                    continue
                payload = json.dumps(task, ensure_ascii=False)
                query = f"""
                DECLARE $task_id AS Utf8;
                DECLARE $payload AS Utf8;
                UPSERT INTO `{self.table_path}` (task_id, payload)
                VALUES ($task_id, $payload);
                """
                prepared = session.prepare(query)
                session.transaction().execute(
                    prepared,
                    {
                        "$task_id": task_id,
                        "$payload": payload,
                    },
                    commit_tx=True,
                )
                inserted += 1

        self._session_pool.retry_operation_sync(_upsert)
        return {"tasks_upserted": inserted, "backend": "ydb", "table_path": self.table_path}

    def list_tasks(self) -> list[dict[str, Any]]:
        self._ensure_client()
        rows: list[dict[str, Any]] = []

        def _load(session) -> list[dict[str, Any]]:
            query = f"SELECT task_id, payload FROM `{self.table_path}`;"
            result_sets = session.transaction().execute(query, commit_tx=True)
            loaded: list[dict[str, Any]] = []
            if not result_sets:
                return loaded
            for row in result_sets[0].rows:
                payload_text = str(getattr(row, "payload", "") or "")
                if not payload_text:
                    continue
                try:
                    payload = json.loads(payload_text)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                task_id = str(getattr(row, "task_id", "") or payload.get("task_id", "")).strip()
                if task_id:
                    payload.setdefault("task_id", task_id)
                loaded.append(payload)
            return loaded

        rows = self._session_pool.retry_operation_sync(_load)
        return rows


class DualWriteOperationalStore:
    """Store wrapper that writes to both primary and secondary backends.

    Secondary backend failures are soft by design and do not break primary write path.
    """

    def __init__(self, primary: OperationalStore, secondary: OperationalStore) -> None:
        self.primary = primary
        self.secondary = secondary

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        primary_result = self.primary.upsert_tasks(tasks)
        secondary_error: str | None = None
        secondary_result: dict[str, Any] | None = None
        try:
            secondary_result = self.secondary.upsert_tasks(tasks)
        except Exception as exc:
            secondary_error = str(exc)
        result: dict[str, Any] = {
            "backend": "dual_write",
            "primary_result": primary_result,
            "secondary_result": secondary_result,
            "secondary_error": secondary_error,
        }
        return result

    def list_tasks(self) -> list[dict[str, Any]]:
        return self.primary.list_tasks()


def build_operational_store(
    mode: str,
    *,
    env_name: str,
    ydb_endpoint: str,
    ydb_database: str,
    json_file_path: str,
) -> OperationalStore:
    """Select store backend for current rollout mode.

    Rules:
    - `legacy`: JSON adapter.
    - `dual_write`: JSON primary + YDB secondary; in prod YDB config is required.
    - `ydb_primary`: YDB preferred; fallback to JSON only in non-prod.
    - `ydb_only`: hard-fail in prod when YDB config missing; fallback to JSON only in dev/test.
    """
    mode = (mode or "legacy").strip().lower()
    env_name = (env_name or "dev").strip().lower()
    json_store = JsonOperationalStore(file_path=json_file_path)
    has_ydb = bool(ydb_endpoint.strip() and ydb_database.strip())

    if mode == "legacy":
        return json_store

    if mode == "dual_write":
        if not has_ydb:
            if env_name == "prod":
                raise RuntimeError("STORE_MODE=dual_write requires YDB config in prod.")
            return json_store
        ydb_store = YdbOperationalStore(endpoint=ydb_endpoint, database=ydb_database)
        return DualWriteOperationalStore(primary=json_store, secondary=ydb_store)

    if mode in {"ydb_primary", "ydb_only"}:
        if has_ydb:
            return YdbOperationalStore(endpoint=ydb_endpoint, database=ydb_database)
        if env_name == "prod":
            raise RuntimeError(f"STORE_MODE={mode} requires YDB config in prod.")
        return json_store

    return json_store

"""Operational store adapters.

YDB (serverless, gRPC SDK) is the primary migration target.
JSON-backed adapter remains for local tests/mocks only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class OperationalStore(Protocol):
    """Store contract for normalized task upserts."""

    def upsert_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]: ...


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


def build_operational_store(
    mode: str,
    *,
    ydb_endpoint: str,
    ydb_database: str,
    json_file_path: str,
) -> OperationalStore:
    """Select store backend for current rollout mode.

    Rules:
    - `legacy`: caller should avoid writes, but we return JSON fallback.
    - `dual_write` / `ydb_primary` / `ydb_only`: prefer YDB when endpoint+db provided.
    - when YDB settings are missing, fallback to JSON (local/mock contour).
    """
    mode = (mode or "legacy").strip().lower()
    if mode in {"dual_write", "ydb_primary", "ydb_only"} and ydb_endpoint.strip() and ydb_database.strip():
        return YdbOperationalStore(endpoint=ydb_endpoint, database=ydb_database)
    return JsonOperationalStore(file_path=json_file_path)

"""YDB repository for frontend v2 readmodel snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.adapters.ydb.client import YdbClient
from src.adapters.ydb.schema import ensure_tables


def _stable_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class FrontendReadmodelRow:
    readmodel_id: str
    contract_version: str
    payload_json: str
    payload_hash: str
    built_from_source_hash: str
    generated_at_utc: datetime | None

    def payload(self) -> dict[str, Any]:
        data = json.loads(self.payload_json)
        return data if isinstance(data, dict) else {}


class FrontendReadmodelRepo:
    """Store and fetch v2 frontend payload snapshot by readmodel id."""

    def __init__(
        self,
        *,
        endpoint: str,
        database: str,
        readmodel_table: str = "dtm_readmodel_frontend_v2",
        tasks_table: str = "dtm_tasks",
        milestones_table: str = "dtm_task_milestones",
        sync_state_table: str = "dtm_sync_state",
        ensure_schema: bool = False,
    ) -> None:
        self.client = YdbClient(endpoint=endpoint, database=database)
        self.readmodel_table = readmodel_table
        if ensure_schema:
            ensure_tables(
                self.client,
                tasks_table=tasks_table,
                milestones_table=milestones_table,
                sync_state_table=sync_state_table,
                readmodel_table=readmodel_table,
            )

    def get_readmodel(self, readmodel_id: str = "frontend_v2:default") -> FrontendReadmodelRow | None:
        query = f"""
        DECLARE $readmodel_id AS Utf8;
        SELECT readmodel_id, contract_version, payload_json, payload_hash, built_from_source_hash, generated_at_utc
        FROM `{self.readmodel_table}`
        WHERE readmodel_id = $readmodel_id;
        """
        result_sets = self.client.execute(query, {"$readmodel_id": str(readmodel_id).strip()})
        if not result_sets or not result_sets[0].rows:
            return None
        row = result_sets[0].rows[0]
        return FrontendReadmodelRow(
            readmodel_id=str(getattr(row, "readmodel_id", "")),
            contract_version=str(getattr(row, "contract_version", "")),
            payload_json=str(getattr(row, "payload_json", "{}")),
            payload_hash=str(getattr(row, "payload_hash", "")),
            built_from_source_hash=str(getattr(row, "built_from_source_hash", "")),
            generated_at_utc=getattr(row, "generated_at_utc", None),
        )

    def upsert_readmodel(
        self,
        payload: dict[str, Any],
        *,
        readmodel_id: str = "frontend_v2:default",
        contract_version: str = "2.0.1",
        built_from_source_hash: str,
    ) -> FrontendReadmodelRow:
        payload_hash = _stable_hash(payload)
        payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        query = f"""
        DECLARE $readmodel_id AS Utf8;
        DECLARE $contract_version AS Utf8;
        DECLARE $payload_json AS Utf8;
        DECLARE $payload_hash AS Utf8;
        DECLARE $built_from_source_hash AS Utf8;
        DECLARE $generated_at_utc AS Timestamp;
        UPSERT INTO `{self.readmodel_table}` (
            readmodel_id, contract_version, payload_json, payload_hash, built_from_source_hash, generated_at_utc
        )
        VALUES (
            $readmodel_id, $contract_version, $payload_json, $payload_hash, $built_from_source_hash, $generated_at_utc
        );
        """
        now = datetime.now(timezone.utc)
        self.client.execute(
            query,
            {
                "$readmodel_id": str(readmodel_id).strip(),
                "$contract_version": contract_version,
                "$payload_json": payload_json,
                "$payload_hash": payload_hash,
                "$built_from_source_hash": built_from_source_hash,
                "$generated_at_utc": now,
            },
        )
        return FrontendReadmodelRow(
            readmodel_id=str(readmodel_id).strip(),
            contract_version=contract_version,
            payload_json=payload_json,
            payload_hash=payload_hash,
            built_from_source_hash=built_from_source_hash,
            generated_at_utc=now,
        )

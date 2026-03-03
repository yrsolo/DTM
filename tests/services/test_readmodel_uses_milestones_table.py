"""Ensure readmodel builder uses milestones table rows as source of timing."""

from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone

from src.services.readmodel_builder import FrontendReadmodelBuilderService


@dataclass
class _SyncState:
    source_hash: str
    last_success_at_utc: datetime


class _OperationalRepoStub:
    def __init__(self) -> None:
        self.client = type("Client", (), {"stats": type("Stats", (), {"ydb_queries_count": 2})()})()
        self.task_versions = None

    def get_sync_state(self, source_id: str):  # noqa: ARG002
        return _SyncState(source_hash="hash-1", last_success_at_utc=datetime.now(timezone.utc))

    def list_tasks(self, *, statuses=None):  # noqa: ANN001, ARG002
        return [
            {
                "task_id": "42",
                "title": "Task 42",
                "brand": "Brand",
                "format_": "Format",
                "customer": "Customer",
                "raw_timing": "raw",
                "owner_id": "Designer",
                "group_id": "Project",
                "status": "work",
                "current_version": 3,
            }
        ]

    def list_milestones_for_versions(self, *, task_versions=None):  # noqa: ANN001
        self.task_versions = task_versions
        return [
            {
                "task_id": "42",
                "version": 3,
                "idx": 1,
                "type": "storyboard",
                "planned_date": "2026-03-04",
                "status": "planned",
            },
            {
                "task_id": "42",
                "version": 3,
                "idx": 2,
                "type": "animatic",
                "planned_date": "2026-03-11",
                "status": "planned",
            },
        ]


class _ReadmodelRepoStub:
    def __init__(self) -> None:
        self.client = type("Client", (), {"stats": type("Stats", (), {"ydb_queries_count": 1})()})()
        self.saved_payload = None

    def get_readmodel(self, readmodel_id: str):  # noqa: ARG002
        return None

    def upsert_readmodel(self, payload, *, readmodel_id, contract_version, built_from_source_hash):  # noqa: ANN001
        self.saved_payload = payload
        return type(
            "Row",
            (),
            {
                "readmodel_id": readmodel_id,
                "payload_json": json.dumps(payload, ensure_ascii=False),
                "payload_hash": "sha256:test",
                "built_from_source_hash": built_from_source_hash,
            },
        )()


class ReadmodelUsesMilestonesTableTestCase(unittest.TestCase):
    def test_builder_populates_task_milestones_from_rows(self) -> None:
        operational_repo = _OperationalRepoStub()
        readmodel_repo = _ReadmodelRepoStub()
        service = FrontendReadmodelBuilderService(
            operational_repo=operational_repo,  # type: ignore[arg-type]
            readmodel_repo=readmodel_repo,  # type: ignore[arg-type]
            source_id="sheet:test",
            env_name="test",
            source_sheet_name="Sheet",
        )

        result = service.run(readmodel_id="frontend_v2:default")

        self.assertTrue(result.changed)
        self.assertEqual(result.tasks_count, 1)
        self.assertEqual(operational_repo.task_versions, {"42": 3})
        tasks = readmodel_repo.saved_payload["tasks"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(tasks[0]["milestones"]), 2)
        self.assertEqual(tasks[0]["milestones"][0]["type"], "storyboard")
        self.assertEqual(tasks[0]["milestones"][1]["type"], "animatic")


if __name__ == "__main__":
    unittest.main()

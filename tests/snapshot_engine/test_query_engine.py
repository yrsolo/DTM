from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from src.snapshot_engine.model import AttachmentMeta, PrepIndexes, PrepSnapshot, TaskExtra, TaskSheet, TaskView
from src.snapshot_engine.query_engine import FrontendV2Query, SnapshotQueryEngine


def _sheet(*, task_id: str, status: str, history: str, owner: str, group: str, milestone_day: str) -> TaskSheet:
    return TaskSheet(
        task_id=task_id,
        title=task_id,
        owner_id=owner,
        group_id=group,
        brand="brand",
        format_="format",
        customer="customer",
        raw_timing="raw",
        status=status,
        history=history,
        timing={milestone_day: ["feedback"]},
    )


class SnapshotQueryEngineTestCase(unittest.TestCase):
    def test_query_frontend_v2_applies_filters_and_keeps_history(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": TaskView(sheet=_sheet(task_id="t1", status="work", history="h1", owner="Alice", group="G", milestone_day="2026-03-10")),
                "t2": TaskView(sheet=_sheet(task_id="t2", status="done", history="h2", owner="Bob", group="G", milestone_day="2026-03-11")),
            },
            indexes=PrepIndexes(),
        )
        engine = SnapshotQueryEngine(env_name="dev", source_sheet_name="Sheet")
        payload = engine.query_frontend_v2(
            prep,
            FrontendV2Query(
                statuses=["work"],
                designer="",
                limit=10,
                include_people=True,
                window_enabled=False,
                window_start=None,
                window_end=None,
            ),
        )

        self.assertEqual(payload["meta"]["readmodelSource"], "s3_snapshot")
        self.assertEqual(payload["summary"]["tasksReturned"], 1)
        self.assertEqual(payload["tasks"][0]["id"], "t1")
        self.assertEqual(payload["tasks"][0]["history"], "h1")

    def test_query_frontend_v2_exposes_attachment_metadata_without_storage_key(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": TaskView(
                    sheet=_sheet(task_id="t1", status="work", history="h1", owner="Alice", group="G", milestone_day="2026-03-10"),
                    extra=TaskExtra(
                        task_id="t1",
                        attachments=[
                            AttachmentMeta(
                                id="a1",
                                key="attachments/test/t1/a1-file.docx",
                                filename="file.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                size=123,
                                uploaded_at_utc=datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
                                uploaded_by="Alice",
                                kind="docx",
                                status="ready",
                                snapshot_visible=True,
                            )
                        ],
                    ),
                )
            },
            indexes=PrepIndexes(),
        )
        engine = SnapshotQueryEngine(env_name="dev", source_sheet_name="Sheet")
        payload = engine.query_frontend_v2(
            prep,
            FrontendV2Query(
                statuses=["work"],
                designer="",
                limit=10,
                include_people=True,
                window_enabled=False,
                window_start=None,
                window_end=None,
            ),
        )
        self.assertEqual(payload["tasks"][0]["attachments"][0]["name"], "file.docx")
        self.assertEqual(payload["tasks"][0]["attachments"][0]["kind"], "docx")
        self.assertEqual(payload["tasks"][0]["attachments"][0]["status"], "ready")
        self.assertNotIn("key", payload["tasks"][0]["attachments"][0])

    def test_query_frontend_v2_window_filter(self) -> None:
        prep = PrepSnapshot(
            source_id="sheet:test",
            raw_source_hash="hash",
            built_at_utc=datetime.now(timezone.utc),
            tasks_by_id={
                "t1": TaskView(sheet=_sheet(task_id="t1", status="work", history="h1", owner="Alice", group="G", milestone_day="2026-03-10")),
                "t2": TaskView(sheet=_sheet(task_id="t2", status="work", history="h2", owner="Bob", group="G", milestone_day="2026-04-15")),
            },
            indexes=PrepIndexes(),
        )
        engine = SnapshotQueryEngine(env_name="dev", source_sheet_name="Sheet")
        payload = engine.query_frontend_v2(
            prep,
            FrontendV2Query(
                statuses=["work"],
                designer="",
                limit=10,
                include_people=False,
                window_enabled=True,
                window_start=date(2026, 3, 1),
                window_end=date(2026, 3, 31),
            ),
        )
        self.assertEqual(payload["summary"]["tasksReturned"], 1)
        self.assertEqual(payload["tasks"][0]["id"], "t1")


if __name__ == "__main__":
    unittest.main()

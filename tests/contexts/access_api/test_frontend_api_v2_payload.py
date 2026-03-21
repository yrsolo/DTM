"""Tests for frontend API v2 payload contract 2.0.1."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.contexts.access_api.internal.frontend_payload_v2 import build_frontend_api_payload_v2


SNAPSHOT_BASE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "access_api" / "frontend_v2_payload.json"
SNAPSHOT_WINDOW_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "access_api" / "frontend_v2_payload_window.json"


def _tasks() -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            id=101,
            name="Task Alpha",
            designer="Designer One",
            status="work",
            color_status="work",
            brand="BrandA",
            format_="Banner",
            project_name="Project X",
            customer="Cust",
            min_date=pd.Timestamp("2026-03-02"),
            max_date=pd.Timestamp("2026-03-15"),
            timing={
                pd.Timestamp("2026-03-03"): ["раскадровка"],
                pd.Timestamp("2026-03-11"): ["аниматик"],
            },
        ),
        SimpleNamespace(
            id=102,
            name="Task Beta",
            designer="Designer Two",
            status="pre_done",
            color_status="pre_done",
            brand="BrandB",
            format_="Video",
            project_name="Project Y",
            customer="Cust",
            min_date=pd.Timestamp("2026-04-10"),
            max_date=pd.Timestamp("2026-04-20"),
            timing={
                pd.Timestamp("2026-04-12"): ["финал/сдача"],
            },
        ),
    ]


def _people() -> list[SimpleNamespace]:
    return [
        SimpleNamespace(id="p1", name="Designer One", position="designer", vacation=""),
        SimpleNamespace(id="p2", name="Designer Two", position="designer", vacation=""),
    ]


class FrontendApiV2PayloadTestCase(unittest.TestCase):
    def _build_payload(self, **kwargs) -> dict[str, object]:
        with patch("src.core.task_query_contract.pd.Timestamp.today", return_value=pd.Timestamp("2026-03-01")):
            return build_frontend_api_payload_v2(**kwargs)

    def test_payload_has_required_top_level_structure(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        for key in ("meta", "filters", "summary", "entities", "tasks"):
            self.assertIn(key, payload)
        self.assertEqual(payload["meta"]["artifact"], "dtm_frontend_api_v2")
        self.assertEqual(payload["meta"]["contractVersion"], "2.0.1")
        self.assertIsInstance(payload["tasks"], list)
        self.assertTrue(all("milestones" in item for item in payload["tasks"]))
        self.assertTrue(all("history" in item for item in payload["tasks"]))
        self.assertTrue(all(isinstance(item["history"], str) for item in payload["tasks"]))

    def test_milestone_type_enum_contains_only_used_types(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        milestone_types = payload["entities"]["enums"]["milestoneType"]
        self.assertIn("storyboard", milestone_types)
        self.assertIn("animatic", milestone_types)
        self.assertIn("final", milestone_types)
        self.assertNotIn("draft", milestone_types)

    def test_window_filter_by_task_dates(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            window_start=date(2026, 3, 1),
            window_end=date(2026, 3, 31),
            window_mode="intersects",
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(payload["summary"]["tasksTotal"], 2)
        self.assertEqual(payload["summary"]["tasksReturned"], 1)
        self.assertEqual(payload["tasks"][0]["id"], "101")
        self.assertGreaterEqual(len(payload["tasks"][0]["milestones"]), 2)

    def test_payload_matches_snapshot_default(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        expected = json.loads(SNAPSHOT_BASE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload, expected)

    def test_payload_matches_snapshot_with_window(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            window_start=date(2026, 3, 1),
            window_end=date(2026, 3, 31),
            window_mode="intersects",
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        expected = json.loads(SNAPSHOT_WINDOW_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload, expected)

    def test_owner_ids_reference_people_entities_when_people_included(self) -> None:
        payload = self._build_payload(
            tasks=_tasks(),
            people=_people(),
            env_name="test",
            source_sheet_name="SourceSheet",
            statuses=["work", "pre_done"],
            limit=100,
            include_people=True,
            generated_at=datetime(2026, 3, 2, 20, 0, 0, tzinfo=timezone.utc),
            synced_at=datetime(2026, 3, 2, 19, 30, 0, tzinfo=timezone.utc),
        )
        people_ids = {item["id"] for item in payload["entities"]["people"]}
        for task in payload["tasks"]:
            self.assertIn(task["ownerId"], people_ids)


if __name__ == "__main__":
    unittest.main()



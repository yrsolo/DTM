"""Tests for frontend API v2 payload contract and snapshot stability."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.api_payload_v2 import build_frontend_api_payload_v2


SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "snapshots" / "frontend_v2_payload.json"


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
            min_date=None,
            max_date=None,
            timing={},
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
            min_date=None,
            max_date=None,
            timing={},
        ),
    ]


def _people() -> list[SimpleNamespace]:
    return [
        SimpleNamespace(id="p1", name="Designer One", position="designer", vacation=""),
        SimpleNamespace(id="p2", name="Designer Two", position="designer", vacation=""),
    ]


class FrontendApiV2PayloadTestCase(unittest.TestCase):
    def test_payload_has_required_top_level_structure(self) -> None:
        payload = build_frontend_api_payload_v2(
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
        self.assertEqual(payload["meta"]["contractVersion"], "2.0.0")
        self.assertIsInstance(payload["tasks"], list)

    def test_payload_matches_snapshot(self) -> None:
        payload = build_frontend_api_payload_v2(
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
        expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload, expected)


if __name__ == "__main__":
    unittest.main()

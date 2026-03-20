from __future__ import annotations

import unittest
from datetime import date
from types import SimpleNamespace

import pandas as pd

from src.contexts.snapshot.internal.engine.model import SheetSnapshot
from src.contexts.snapshot.internal.engine.update_job import SheetsTaskNormalizer


class SheetsTaskNormalizerTestCase(unittest.TestCase):
    def test_normalize_keeps_history_and_color_status(self) -> None:
        normalizer = SheetsTaskNormalizer()
        task = SimpleNamespace(
            id="task-1",
            name="Task 1",
            designer="Designer",
            project_name="Group",
            brand="Brand",
            format_="Format",
            customer="Customer",
            raw_timing="raw",
            status="raw history",
            color_status="work",
            timing={pd.Timestamp("2026-03-10"): ["feedback"]},
        )

        raw = normalizer.normalize(
            source_id="sheet:test",
            source_hash="hash",
            snapshot=SheetSnapshot(worksheet_range="A1:Z2000", values=[], colors=[]),
            tasks=[task],
        )
        row = raw.tasks_by_id["task-1"]
        self.assertEqual(row.history, "raw history")
        self.assertEqual(row.status, "work")
        self.assertIn("2026-03-10", row.timing)
        self.assertEqual(row.milestones[0].planned, date(2026, 3, 10))

    def test_normalize_adds_synthetic_start_when_timing_missing(self) -> None:
        normalizer = SheetsTaskNormalizer()
        task = SimpleNamespace(
            id="task-2",
            name="Task 2",
            designer="Designer",
            project_name="Group",
            brand="Brand",
            format_="Format",
            customer="Customer",
            raw_timing="",
            status="raw",
            color_status="pre_done",
            timing={},
        )
        raw = normalizer.normalize(
            source_id="sheet:test",
            source_hash="hash",
            snapshot=SheetSnapshot(worksheet_range="A1:Z2000", values=[], colors=[]),
            tasks=[task],
        )
        row = raw.tasks_by_id["task-2"]
        self.assertEqual(len(row.timing), 1)
        self.assertEqual(list(row.timing.values())[0], ["start"])


if __name__ == "__main__":
    unittest.main()

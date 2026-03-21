"""Tests for shared task query contract used by API/render/reminders."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) in sys.path:
    sys.path.remove(str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR))

from src.core.task_query_contract import TimeWindow, apply_task_query, milestones_in_window, project_tasks, query_source_tasks


class TaskQueryContractTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tasks = [
            SimpleNamespace(
                id="1",
                name="Alpha",
                designer="Designer A",
                status="work",
                color_status="work",
                brand="B",
                format_="F",
                project_name="P1",
                customer="C",
                raw_timing="",
                timing={pd.Timestamp("2026-03-10"): ["раскадровка"]},
            ),
            SimpleNamespace(
                id="2",
                name="Beta",
                designer="Designer B",
                status="done",
                color_status="done",
                brand="B",
                format_="F",
                project_name="P2",
                customer="C",
                raw_timing="",
                timing={pd.Timestamp("2026-04-10"): ["финал"]},
            ),
        ]

    def test_status_designer_and_window_filters(self) -> None:
        projections = project_tasks(self.tasks)
        filtered = apply_task_query(
            projections,
            statuses=["work"],
            designer="Designer A",
            window=TimeWindow(start=date(2026, 3, 1), end=date(2026, 3, 31)),
            limit=100,
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].task_id, "1")

    def test_query_source_tasks_returns_original_objects(self) -> None:
        filtered = query_source_tasks(self.tasks, statuses=["done"], limit=10)
        self.assertEqual(len(filtered), 1)
        self.assertIs(filtered[0], self.tasks[1])

    def test_milestones_window_filter_for_reminders(self) -> None:
        projection = project_tasks(self.tasks)[0]
        selected = milestones_in_window(
            projection,
            TimeWindow(start=date(2026, 3, 10), end=date(2026, 3, 10)),
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].type, "storyboard")


if __name__ == "__main__":
    unittest.main()


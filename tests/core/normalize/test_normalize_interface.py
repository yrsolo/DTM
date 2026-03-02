"""Unit tests for normalize_task interface."""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from src.core.models.contracts import TaskRaw
from src.core.normalize.interface import normalize_task


class NormalizeInterfaceTestCase(unittest.TestCase):
    @staticmethod
    def _fixture_rows() -> list[dict[str, str]]:
        fixture_path = Path("tests/fixtures/normalize/task_raw_samples.json")
        return json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_normalize_task_builds_stable_task_id(self) -> None:
        row = self._fixture_rows()[0]
        raw = TaskRaw(**row)
        normalized = normalize_task(raw, anchor_date=date(2026, 3, 1))
        self.assertEqual(normalized.task_id, "sheet-001:ТАБЛИЧКА:row-10")
        self.assertEqual(normalized.status, "work")
        self.assertEqual(len(normalized.stages), 2)

    def test_normalize_task_infers_cross_year_due_date(self) -> None:
        row = self._fixture_rows()[1]
        raw = TaskRaw(**row)
        normalized = normalize_task(raw, anchor_date=date(2026, 12, 30))
        self.assertEqual(normalized.stages[0].planned_at, date(2026, 12, 31))
        self.assertEqual(normalized.stages[1].planned_at, date(2027, 1, 2))

    def test_normalize_task_keeps_raw_fields_for_debug(self) -> None:
        row = self._fixture_rows()[2]
        raw = TaskRaw(**row)
        normalized = normalize_task(raw, anchor_date=date(2026, 3, 1))
        self.assertIn("stages_raw", normalized.raw_fields)
        self.assertEqual(normalized.raw_fields["stages_raw"], "Стадия xx.yy; Без даты")
        self.assertIsNone(normalized.next_due_at)


if __name__ == "__main__":
    unittest.main()


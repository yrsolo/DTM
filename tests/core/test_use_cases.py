"""Unit tests for planner use-case orchestration switches."""

from __future__ import annotations

import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

USE_CASES_PATH = Path("core/use_cases.py").resolve()
SPEC = spec_from_file_location("dtm_core_use_cases", USE_CASES_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load use-cases module from {USE_CASES_PATH}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
run_planner_use_case = MODULE.run_planner_use_case


class _FakePlanner:
    def __init__(self) -> None:
        self.update_calls = 0
        self.task_to_calendar_calls = 0
        self.designer_task_to_calendar_calls = 0
        self.task_to_table_calls = 0
        self.send_reminders_calls = 0

    def update(self) -> None:
        self.update_calls += 1

    def task_to_calendar(self) -> None:
        self.task_to_calendar_calls += 1

    def designer_task_to_calendar(self) -> None:
        self.designer_task_to_calendar_calls += 1

    def task_to_table(self) -> None:
        self.task_to_table_calls += 1

    async def send_reminders(self) -> None:
        self.send_reminders_calls += 1

    def build_quality_report(self) -> dict[str, int]:
        return {"ok": 1}


class UseCasesTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_sync_branch_is_skipped_when_allow_sync_false(self) -> None:
        planner = _FakePlanner()
        await run_planner_use_case(planner, mode="sync-only", allow_sync=False)
        self.assertEqual(planner.update_calls, 0)
        self.assertEqual(planner.task_to_table_calls, 0)

    async def test_sync_branch_runs_when_allow_sync_true(self) -> None:
        planner = _FakePlanner()
        await run_planner_use_case(planner, mode="sync-only", allow_sync=True)
        self.assertEqual(planner.update_calls, 1)
        self.assertEqual(planner.task_to_table_calls, 1)


if __name__ == "__main__":
    unittest.main()

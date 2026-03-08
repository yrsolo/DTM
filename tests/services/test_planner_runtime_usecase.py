from __future__ import annotations

import unittest

from src.services.usecases.planner_runtime import run_planner_use_case


class _PlannerStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def update(self) -> None:
        self.calls.append("update")

    def task_to_calendar(self) -> None:
        self.calls.append("task_to_calendar")

    def designer_task_to_calendar(self) -> None:
        self.calls.append("designer_task_to_calendar")

    def task_to_table(self) -> None:
        self.calls.append("task_to_table")

    async def send_reminders(self) -> None:
        self.calls.append("send_reminders")

    def build_quality_report(self):  # noqa: ANN001
        self.calls.append("build_quality_report")
        return {"summary": {"task_row_issue_count": 0}}


class PlannerRuntimeUseCaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_sync_path_skips_legacy_calendar_render(self) -> None:
        planner = _PlannerStub()
        report = await run_planner_use_case(planner, mode="timer", allow_sync=True)
        self.assertEqual(report["summary"]["task_row_issue_count"], 0)
        self.assertIn("update", planner.calls)
        self.assertIn("task_to_calendar", planner.calls)
        self.assertIn("task_to_table", planner.calls)
        self.assertNotIn("designer_task_to_calendar", planner.calls)

    async def test_test_mode_still_runs_reminders(self) -> None:
        planner = _PlannerStub()
        await run_planner_use_case(planner, mode="test", allow_sync=False)
        self.assertIn("send_reminders", planner.calls)


if __name__ == "__main__":
    unittest.main()

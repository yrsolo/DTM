from __future__ import annotations

import unittest

from src.platform.runtime.orchestration import (
    planned_trigger_commands,
    resolve_trigger_mode_by_id,
)


class OrchestrationTestCase(unittest.TestCase):
    def test_resolves_trigger_mode_by_id(self) -> None:
        self.assertEqual(resolve_trigger_mode_by_id("trigger-1", {"trigger-1": "timer"}), "timer")

    def test_timer_plan_contains_snapshot_and_render_commands(self) -> None:
        planned = planned_trigger_commands("timer")
        self.assertEqual(
            [command_type for command_type, _payload in planned],
            ["update_snapshot", "render_timeline_sheet", "render_designers_sheet"],
        )

    def test_morning_plan_contains_cleanup_then_reminder_commands(self) -> None:
        planned = planned_trigger_commands("morning")
        self.assertEqual(
            [command_type for command_type, _payload in planned],
            ["cleanup_job_statuses", "send_reminders"],
        )
        self.assertEqual(planned[0][1], {"older_than_hours": 24, "dry_run": False})


if __name__ == "__main__":
    unittest.main()

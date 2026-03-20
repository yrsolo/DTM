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

    def test_morning_plan_contains_reminder_command(self) -> None:
        planned = planned_trigger_commands("morning")
        self.assertEqual([command_type for command_type, _payload in planned], ["send_reminders"])


if __name__ == "__main__":
    unittest.main()

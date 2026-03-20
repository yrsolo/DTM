from __future__ import annotations

import unittest
from datetime import date

from src.contexts.reminders.internal import ReminderFormatter, ReminderGroup
from src.contexts.snapshot.internal.engine.model import TaskSheet, TaskView


def _task(task_id: str, owner: str, day: date, stages: list[str]) -> TaskView:
    return TaskView(
        sheet=TaskSheet(
            task_id=task_id,
            title=f"title-{task_id}",
            owner_id=owner,
            group_id="Проект A",
            brand="Бренд",
            format_="граф. ролик",
            customer="Клиент",
            raw_timing="",
            status="work",
            history="",
            timing={day.isoformat(): stages},
            milestones=[],
        ),
        extra=None,
    )


class ReminderFormatterTestCase(unittest.TestCase):
    def test_builds_today_and_next_sections_and_filters_hidden_stages(self) -> None:
        today = date(2026, 3, 7)
        next_day = date(2026, 3, 9)
        formatter = ReminderFormatter(hidden_stage_names=("клиента",))
        draft = formatter.build_draft(
            ReminderGroup(
                owner_name="Дизайнер",
                tasks_today=[_task("1", "Дизайнер", today, ["аниматик", "ответ клиента"])],
                tasks_next_workday=[_task("2", "Дизайнер", next_day, ["финал"])],
            ),
            today=today,
            next_workday=next_day,
        )
        self.assertIsNotNone(draft)
        text = str(draft.text if draft else "")
        self.assertIn("Задачи на сегодня", text)
        self.assertIn("Задачи на Monday, 09.03", text)
        self.assertIn("аниматик", text)
        self.assertNotIn("ответ клиента", text)


if __name__ == "__main__":
    unittest.main()

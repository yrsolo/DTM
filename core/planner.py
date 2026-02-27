"""
Модуль содержит класс GoogleSheetPlanner.
В Stage 2 wiring зависимостей вынесен в bootstrap-слой.
"""

from config import SOURCE_SHEET_INFO
from core.bootstrap import PlannerDependencies, build_planner_dependencies
from utils.service import GoogleSheetInfo


def build_reminder_sli_summary(reminder_delivery_counters):
    counters = dict(reminder_delivery_counters or {})
    sent = int(counters.get("sent", 0))
    send_errors = int(counters.get("send_errors", 0))
    # Attemptable = entries that reached "send attempt" decision point.
    # Excludes functional skips (no message/person/chat_id/vacation/mock mode).
    reminder_delivery_attemptable_count = sent + send_errors + int(counters.get("skipped_duplicate", 0))
    reminder_delivery_attempted_count = sent + send_errors
    reminder_delivery_rate = (
        round(sent / reminder_delivery_attemptable_count, 4)
        if reminder_delivery_attemptable_count > 0
        else None
    )
    reminder_failure_rate = (
        round(send_errors / reminder_delivery_attemptable_count, 4)
        if reminder_delivery_attemptable_count > 0
        else None
    )

    return {
        "reminder_delivery_attemptable_count": reminder_delivery_attemptable_count,
        "reminder_delivery_attempted_count": reminder_delivery_attempted_count,
        "reminder_delivery_rate": reminder_delivery_rate,
        "reminder_failure_rate": reminder_failure_rate,
    }


class GoogleSheetPlanner:
    def __init__(
            self,
            key_json,
            sheet_info_data,
            mode="test",
            dry_run=False,
            mock_external=False,
            dependencies: PlannerDependencies = None,
    ):
        self.mode = mode
        self.dry_run = dry_run
        self.mock_external = bool(mock_external)
        self.sheet_info = GoogleSheetInfo(**sheet_info_data)
        self.source_sheet_info = GoogleSheetInfo(**SOURCE_SHEET_INFO)
        if dependencies is None:
            dependencies = build_planner_dependencies(
                key_json,
                sheet_info_data,
                dry_run=dry_run,
                mock_external=self.mock_external,
            )

        self.service = dependencies.service
        self.timing_processor = dependencies.timing_processor
        self.task_repository = dependencies.task_repository
        self.task_manager = dependencies.task_manager
        self.calendar_manager = dependencies.calendar_manager
        self.task_calendar_manager = dependencies.task_calendar_manager
        self.openai_agent = dependencies.openai_agent
        self.people_manager = dependencies.people_manager
        self.reminder = dependencies.reminder

    def task_to_table(self, color_status=("work", "pre_done")):
        self.task_manager.task_to_table(color_status)

    def designer_task_to_calendar(self, color_status=("work", "pre_done"), min_date="1W"):
        tasks = self.task_repository.get_task_by_color_status(color_status)
        task_timings = self.timing_processor.create_task_timing_structure(tasks)
        calendar = self.calendar_manager.create_calendar_structure(task_timings)
        self.calendar_manager.write_calendar_to_sheet(calendar, min_date)

    def update(self):
        return self.task_manager.update()

    def task_to_calendar(self, color_status=("wait", "work", "pre_done")):
        self.task_calendar_manager.all_tasks_to_sheet()
        # tasks = self.task_repository.get_task_by_color_status(color_status)
        # task_timings = self.timing_processor.create_task_timing_structure(tasks)
        # calendar = self.task_calendar_manager.create_task_calendar_structure(task_timings)
        # self.task_calendar_manager.write_task_calendar_to_sheet(calendar)

    async def send_reminders(self):
        await self.reminder.get_reminders()
        await self.reminder.send_reminders(mode=self.mode)

    def build_quality_report(self):
        task_row_issues = [str(issue) for issue in getattr(self.task_repository, "row_issues", [])]
        people_row_issues = [str(issue) for issue in getattr(self.people_manager, "row_issues", [])]
        reminder_delivery_counters = getattr(self.reminder, "get_delivery_counters", lambda: {})()
        timing_parse_issues = [
            str(issue) for issue in getattr(self.task_repository.timing_parser, "parse_issues", [])
        ]
        timing_parse_error_count = int(
            getattr(self.task_repository.timing_parser, "total_parse_errors", 0)
        )
        reminder_sli_summary = build_reminder_sli_summary(reminder_delivery_counters)

        return {
            "mode": self.mode,
            "dry_run": bool(self.dry_run),
            "summary": {
                "task_row_issue_count": len(task_row_issues),
                "people_row_issue_count": len(people_row_issues),
                "timing_parse_error_count": timing_parse_error_count,
                "reminder_sent_count": int(reminder_delivery_counters.get("sent", 0)),
                "reminder_send_error_count": int(reminder_delivery_counters.get("send_errors", 0)),
                **reminder_sli_summary,
            },
            "task_row_issues": task_row_issues,
            "people_row_issues": people_row_issues,
            "timing_parse_issues": timing_parse_issues,
            "reminder_delivery_counters": reminder_delivery_counters,
        }

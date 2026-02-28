"""Planner orchestration facade for timer, calendar, and reminder flows."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from config import SOURCE_SHEET_INFO
from core.bootstrap import PlannerDependencies, build_planner_dependencies
from utils.service import GoogleSheetInfo


CounterValue = float | int | None


def _counter_value(counters: Mapping[str, Any], key: str, default: int = 0) -> int:
    """Read integer-like counter values with a safe fallback."""
    raw = counters.get(key, default)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def build_reminder_sli_summary(
    reminder_delivery_counters: Mapping[str, int] | None,
) -> dict[str, CounterValue]:
    """Build high-level reminder delivery SLI counters from raw delivery metrics."""
    counters = dict(reminder_delivery_counters or {})
    sent = _counter_value(counters, "sent")
    send_errors = _counter_value(counters, "send_errors")
    # Attemptable excludes functional skips (no person/chat/message/vacation/mock mode).
    reminder_delivery_attemptable_count = sent + send_errors + _counter_value(counters, "skipped_duplicate")
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
    """Stateful facade around planner dependencies used by CLI and serverless handlers."""

    def __init__(
        self,
        key_json: str,
        sheet_info_data: Mapping[str, str],
        mode: str = "test",
        dry_run: bool = False,
        mock_external: bool = False,
        dependencies: PlannerDependencies | None = None,
    ) -> None:
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

    def task_to_table(self, color_status: Sequence[str] = ("work", "pre_done")) -> None:
        """Render selected task statuses into the destination table."""
        self.task_manager.task_to_table(color_status)

    def designer_task_to_calendar(
        self,
        color_status: Sequence[str] = ("work", "pre_done"),
        min_date: str = "1W",
    ) -> None:
        """Build and publish a calendar view from filtered designer tasks."""
        tasks = self.task_repository.get_task_by_color_status(color_status)
        task_timings = self.timing_processor.create_task_timing_structure(tasks)
        calendar = self.calendar_manager.create_calendar_structure(task_timings)
        self.calendar_manager.write_calendar_to_sheet(calendar, min_date)

    def update(self) -> Any:
        """Run task manager update flow."""
        return self.task_manager.update()

    def task_to_calendar(self, color_status: Sequence[str] = ("wait", "work", "pre_done")) -> None:
        """Render all task calendar rows to sheet (legacy color filter kept for compatibility)."""
        _ = color_status
        self.task_calendar_manager.all_tasks_to_sheet()

    async def send_reminders(self) -> None:
        """Fetch reminder payloads and dispatch notifications."""
        await self.reminder.get_reminders()
        await self.reminder.send_reminders(mode=self.mode)

    def build_quality_report(self) -> dict[str, Any]:
        """Collect runtime quality counters for artifacts and smoke checks."""
        task_row_issues = [str(issue) for issue in getattr(self.task_repository, "row_issues", [])]
        people_row_issues = [str(issue) for issue in getattr(self.people_manager, "row_issues", [])]
        reminder_delivery_counters = getattr(self.reminder, "get_delivery_counters", lambda: {})()
        reminder_enhancement_counters = getattr(self.reminder, "get_enhancement_counters", lambda: {})()
        timing_parse_issues = [
            str(issue) for issue in getattr(self.task_repository.timing_parser, "parse_issues", [])
        ]
        timing_parse_error_count = int(getattr(self.task_repository.timing_parser, "total_parse_errors", 0))
        reminder_sli_summary = build_reminder_sli_summary(reminder_delivery_counters)

        return {
            "mode": self.mode,
            "dry_run": bool(self.dry_run),
            "summary": {
                "task_row_issue_count": len(task_row_issues),
                "people_row_issue_count": len(people_row_issues),
                "timing_parse_error_count": timing_parse_error_count,
                "reminder_sent_count": _counter_value(reminder_delivery_counters, "sent"),
                "reminder_send_error_count": _counter_value(reminder_delivery_counters, "send_errors"),
                "reminder_send_retry_attempt_count": _counter_value(
                    reminder_delivery_counters,
                    "send_retry_attempts",
                ),
                "reminder_send_retry_exhausted_count": _counter_value(
                    reminder_delivery_counters,
                    "send_retry_exhausted",
                ),
                "reminder_send_error_transient_count": _counter_value(
                    reminder_delivery_counters,
                    "send_error_transient",
                ),
                "reminder_send_error_permanent_count": _counter_value(
                    reminder_delivery_counters,
                    "send_error_permanent",
                ),
                "reminder_send_error_unknown_count": _counter_value(
                    reminder_delivery_counters,
                    "send_error_unknown",
                ),
                "reminder_enhancer_provider": reminder_enhancement_counters.get("provider", ""),
                "reminder_enhancer_candidate_count": _counter_value(
                    reminder_enhancement_counters,
                    "candidates_total",
                ),
                "reminder_enhancer_attempt_count": _counter_value(
                    reminder_enhancement_counters,
                    "attempted",
                ),
                "reminder_enhancer_success_count": _counter_value(
                    reminder_enhancement_counters,
                    "succeeded",
                ),
                "reminder_enhancer_fallback_empty_count": _counter_value(
                    reminder_enhancement_counters,
                    "fallback_empty",
                ),
                "reminder_enhancer_fallback_exception_count": _counter_value(
                    reminder_enhancement_counters,
                    "fallback_exception",
                ),
                "reminder_enhancer_skipped_mock_count": _counter_value(
                    reminder_enhancement_counters,
                    "skipped_mock",
                ),
                "reminder_enhancer_failover_mode": reminder_enhancement_counters.get("failover_mode", ""),
                "reminder_enhancer_failover_primary_provider": reminder_enhancement_counters.get(
                    "failover_primary_provider",
                    "",
                ),
                "reminder_enhancer_failover_fallback_provider": reminder_enhancement_counters.get(
                    "failover_fallback_provider",
                    "",
                ),
                "reminder_enhancer_failover_calls": _counter_value(
                    reminder_enhancement_counters,
                    "failover_fallback_calls",
                ),
                "reminder_enhancer_failover_success_count": _counter_value(
                    reminder_enhancement_counters,
                    "failover_fallback_success",
                ),
                **reminder_sli_summary,
            },
            "task_row_issues": task_row_issues,
            "people_row_issues": people_row_issues,
            "timing_parse_issues": timing_parse_issues,
            "reminder_delivery_counters": reminder_delivery_counters,
            "reminder_enhancement_counters": reminder_enhancement_counters,
        }

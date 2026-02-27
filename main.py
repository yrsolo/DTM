"""Основной файл для запуска планировщика задач."""

import asyncio

from config import KEY_JSON, SHEET_INFO, TRIGGERS
from core.bootstrap import build_planner_dependencies
from core.planner import GoogleSheetPlanner
from core.use_cases import resolve_run_mode, run_planner_use_case


def _print_quality_report(report):
    summary = report.get("summary", {})
    print(
        "quality_report_summary="
        f"task_row_issues={summary.get('task_row_issue_count', 0)} "
        f"people_row_issues={summary.get('people_row_issue_count', 0)} "
        f"timing_parse_errors={summary.get('timing_parse_error_count', 0)} "
        f"reminder_sent={summary.get('reminder_sent_count', 0)} "
        f"reminder_send_errors={summary.get('reminder_send_error_count', 0)}"
    )


async def main(**kwargs):
    """Основная функция для запуска планировщика задач.

    Args:
        kwargs: Параметры запуска.
    """
    # ????????????? ????????????
    mode = kwargs.get("mode")
    event = kwargs.get("event")
    dry_run = kwargs.get("dry_run", False)
    mock_external = kwargs.get("mock_external")
    mode = resolve_run_mode(mode=mode, event=event, triggers=TRIGGERS)
    if mock_external is None:
        mock_external = mode == "test"
    print(f"{mode=} {dry_run=} {mock_external=}")

    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=dry_run,
        mock_external=mock_external,
    )
    planner = GoogleSheetPlanner(
        KEY_JSON,
        SHEET_INFO,
        mode=mode,
        dry_run=dry_run,
        mock_external=mock_external,
        dependencies=dependencies,
    )

    quality_report = await run_planner_use_case(planner, mode)
    _print_quality_report(quality_report)
    return quality_report


if __name__ == "__main__":
    asyncio.run(main())

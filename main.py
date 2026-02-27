"""Основной файл для запуска планировщика задач."""

import asyncio

import pandas as pd

from config import KEY_JSON, SHEET_INFO, TRIGGERS
from core.bootstrap import build_planner_dependencies
from core.planner import GoogleSheetPlanner


def _print_quality_report(report):
    summary = report.get("summary", {})
    print(
        "quality_report_summary="
        f"task_row_issues={summary.get('task_row_issue_count', 0)} "
        f"people_row_issues={summary.get('people_row_issue_count', 0)} "
        f"timing_parse_errors={summary.get('timing_parse_error_count', 0)}"
    )


async def main(**kwargs):
    """Основная функция для запуска планировщика задач.

    Args:
        kwargs: Параметры запуска.
    """
    # ????????????? ????????????
    mode = kwargs.get("mode", None)
    event = kwargs.get("event", None)
    dry_run = kwargs.get("dry_run", False)
    mock_external = kwargs.get("mock_external")
    if mode:
        pass
    elif event:
        print(f"{event=}")
        if event == "morning":
            mode = "morning"
        else:
            trigger_id = event["messages"][0]["details"]["trigger_id"]
            mode = TRIGGERS.get(trigger_id, "test")
            print(f"{trigger_id=}")
    else:
        mode = "test"
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

    if mode in {"timer", "test", "sync-only"}:
        start_time = pd.Timestamp.now()
        planner.update()
        planner.task_to_calendar()  # Генерация и запись календаря задач
        planner.designer_task_to_calendar()  # Генерация и запись календаря дизайнеров
        planner.task_to_table()  # Запись задач в лист "Дизайнеры"
        run_time = pd.Timestamp.now() - start_time
        print(f"Table update runtime: {run_time}")

    if mode in {"morning", "test", "reminders-only"}:
        start_time = pd.Timestamp.now()
        now = pd.Timestamp.now(tz="Europe/Moscow")
        dow = now.dayofweek
        if dow in {0, 1, 2, 3, 4} or mode == "test":
            await planner.send_reminders()
        run_time = pd.Timestamp.now() - start_time
        print(f"Reminder runtime: {run_time}")

    quality_report = planner.build_quality_report()
    _print_quality_report(quality_report)
    return quality_report


if __name__ == "__main__":
    asyncio.run(main())

"""Task source switch helper for main job flow."""

from __future__ import annotations

from typing import Any, Callable

from src.adapters.ydb.task_repository import YdbOperationalTaskRepository
from src.services.source_policy import build_source_policy_matrix


def apply_task_source_switches(
    *,
    planner: Any,
    mode: str,
    render_source: str,
    notify_source: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str | None,
    ydb_sa_key_file: str | None,
    log: Callable[[str], None] = print,
) -> tuple[bool, bool]:
    policy = build_source_policy_matrix(
        readmodel_source="legacy",
        notify_source=notify_source,
        render_source=render_source,
    )
    render_reads_ydb = policy.render_reads_ydb(mode)
    notify_reads_ydb = policy.notify_reads_ydb(mode)
    if not (render_reads_ydb or notify_reads_ydb):
        return False, False

    ydb_repository = YdbOperationalTaskRepository(
        endpoint=ydb_endpoint,
        database=ydb_database,
        sa_json_credentials=ydb_sa_json_credentials,
        sa_key_file=ydb_sa_key_file,
    )
    if render_reads_ydb:
        planner.task_repository = ydb_repository
        planner.task_manager.repository = ydb_repository
        planner.calendar_manager.repository = ydb_repository
        planner.task_calendar_manager.repository = ydb_repository
        log("render_source_switch=applied source=ydb")
    if notify_reads_ydb:
        planner.reminder.task_repository = ydb_repository
        log("notify_source_switch=applied source=ydb")
    return render_reads_ydb, notify_reads_ydb

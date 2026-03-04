"""Task source switch helper for main job flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.adapters.ydb.task_repository import YdbOperationalTaskRepository
from src.services.source_policy import build_source_policy_matrix


@dataclass(frozen=True)
class SourceSwitchRequest:
    planner: Any
    mode: str
    render_source: str
    notify_source: str
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    log: Callable[[str], None] = print
    repository_cls: type[YdbOperationalTaskRepository] = YdbOperationalTaskRepository


def apply_task_source_switches(request: SourceSwitchRequest) -> tuple[bool, bool]:
    policy = build_source_policy_matrix(
        readmodel_source="legacy",
        notify_source=request.notify_source,
        render_source=request.render_source,
    )
    render_reads_ydb = policy.render_reads_ydb(request.mode)
    notify_reads_ydb = policy.notify_reads_ydb(request.mode)
    if not (render_reads_ydb or notify_reads_ydb):
        return False, False

    ydb_repository = request.repository_cls(
        endpoint=request.ydb_endpoint,
        database=request.ydb_database,
        sa_json_credentials=request.ydb_sa_json_credentials,
        sa_key_file=request.ydb_sa_key_file,
    )
    if render_reads_ydb:
        request.planner.task_repository = ydb_repository
        request.planner.task_manager.repository = ydb_repository
        request.planner.calendar_manager.repository = ydb_repository
        request.planner.task_calendar_manager.repository = ydb_repository
        request.log("render_source_switch=applied source=ydb")
    if notify_reads_ydb:
        request.planner.reminder.task_repository = ydb_repository
        request.log("notify_source_switch=applied source=ydb")
    return render_reads_ydb, notify_reads_ydb

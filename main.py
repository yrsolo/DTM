"""Основной файл для запуска планировщика задач."""

import asyncio
import hashlib
import json
import traceback
from pathlib import Path

from config import (
    KEY_JSON,
    LEGACY_BLOB_WRITE,
    MIGRATION_ENABLE_SOURCE_HASH_GATE,
    MIGRATION_HASH_GATE_STATE_FILE,
    MIGRATION_STORE_FILE,
    NOTIFY_SOURCE,
    RENDER_SOURCE,
    STORE_MODE,
    RUNTIME_ENV,
    YDB_MIGRATE_ON_START,
    YDB_DATABASE,
    YDB_ENDPOINT,
    SHEET_INFO,
    TRIGGERS,
)
from core.bootstrap import build_planner_dependencies
from core.planner import GoogleSheetPlanner
from core.use_cases import resolve_run_mode, run_planner_use_case
from src.adapters.store_ydb import StoreTaskRepository, build_operational_store
from src.adapters.ydb.operational_repo import OperationalTaskRepo
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.adapters.ydb.schema import ensure_tables
from src.adapters.ydb.client import YdbClient
from src.services.readmodel_builder import FrontendReadmodelBuilderService
from src.services.sync_service import YdbSyncService
from src.services.sync.hash_basis import build_hash_basis
from src.services.sync.hash_gate import evaluate_hash_gate, save_last_hash


def _print_quality_report(report):
    summary = report.get("summary", {})
    print(
        "quality_report_summary="
        f"task_row_issues={summary.get('task_row_issue_count', 0)} "
        f"people_row_issues={summary.get('people_row_issue_count', 0)} "
        f"timing_parse_errors={summary.get('timing_parse_error_count', 0)} "
        f"reminder_sent={summary.get('reminder_sent_count', 0)} "
        f"reminder_send_errors={summary.get('reminder_send_error_count', 0)} "
        f"reminder_retry_attempts={summary.get('reminder_send_retry_attempt_count', 0)} "
        f"reminder_retry_exhausted={summary.get('reminder_send_retry_exhausted_count', 0)} "
        f"reminder_enhancer_provider={summary.get('reminder_enhancer_provider', '')} "
        f"reminder_enhancer_failover_mode={summary.get('reminder_enhancer_failover_mode', '')} "
        f"reminder_enhancer_attempted={summary.get('reminder_enhancer_attempt_count', 0)} "
        f"reminder_enhancer_fallback_empty={summary.get('reminder_enhancer_fallback_empty_count', 0)} "
        f"reminder_attemptable={summary.get('reminder_delivery_attemptable_count')} "
        f"reminder_delivery_rate={summary.get('reminder_delivery_rate')} "
        f"reminder_failure_rate={summary.get('reminder_failure_rate')}"
    )


def _safe_print(text: str) -> None:
    print(str(text).encode("ascii", "backslashreplace").decode("ascii"))


def _task_to_store_record(task) -> dict[str, object]:
    timing_rows = []
    for dt, stages in sorted(task.timing.items(), key=lambda item: item[0]):
        timing_rows.append(
            {
                "date": dt.date().isoformat(),
                "stages": list(stages),
            }
        )
    return {
        "task_id": str(task.id),
        "name": task.name,
        "brand": task.brand,
        "format_": task.format_,
        "project_name": task.project_name,
        "customer": task.customer,
        "designer": task.designer,
        "status": task.status,
        "color_status": task.color_status,
        "raw_timing": task.raw_timing,
        "timing": timing_rows,
    }


def _task_to_operational_payload(task) -> dict[str, object]:
    milestones = []
    for idx, (dt, stages) in enumerate(sorted(task.timing.items(), key=lambda item: item[0])):
        planned = dt.date().isoformat()
        for stage in stages:
            milestones.append(
                {
                    "idx": idx,
                    "type": str(stage).strip().lower() or "unknown",
                    "planned": planned,
                    "actual": None,
                    "status": "planned",
                    "raw_text": str(stage),
                }
            )

    start_date = task.min_date.date().isoformat() if task.min_date is not None else None
    end_date = task.max_date.date().isoformat() if task.max_date is not None else None
    next_due_date = task.min_date.date().isoformat() if task.min_date is not None else None
    task_hash_basis = {
        "id": str(task.id),
        "name": task.name,
        "brand": task.brand,
        "format_": task.format_,
        "project_name": task.project_name,
        "customer": task.customer,
        "designer": task.designer,
        "status": task.color_status,
        "raw_timing": task.raw_timing,
        "milestones": milestones,
    }
    task_hash = hashlib.sha256(
        json.dumps(task_hash_basis, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "task_id": str(task.id),
        "title": task.name,
        "brand": task.brand,
        "format_": task.format_,
        "customer": task.customer,
        "raw_timing": task.raw_timing,
        "owner_id": task.designer,
        "group_id": task.project_name,
        "status": task.color_status,
        "start_date": start_date,
        "end_date": end_date,
        "next_due_date": next_due_date,
        "tags": [],
        "links": {},
        "task_hash": task_hash,
        "task_revision": 1,
        "raw_payload": task_hash_basis,
        "milestones": milestones,
    }


def _read_source_range_values(source_task_repository) -> list[list[str]]:
    spreadsheet_name = source_task_repository.source_sheet_info.spreadsheet_name
    sheet_name = source_task_repository.source_sheet_info.get_sheet_name("tasks")
    return source_task_repository.service.get_worksheet_values(
        spreadsheet_name=spreadsheet_name,
        worksheet_name=sheet_name,
        worksheet_range="A1:Z2000",
    )


def _build_ydb_task_repository() -> StoreTaskRepository:
    read_store = build_operational_store(
        "ydb_only",
        env_name=RUNTIME_ENV,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        json_file_path=MIGRATION_STORE_FILE,
    )
    return StoreTaskRepository(read_store)


def _apply_task_source_switches(planner: GoogleSheetPlanner, mode: str) -> tuple[bool, bool]:
    render_reads_ydb = RENDER_SOURCE == "ydb" and mode in {"timer", "test", "sync-only"}
    notify_reads_ydb = NOTIFY_SOURCE == "ydb" and mode in {"morning", "test", "reminders-only"}
    if not (render_reads_ydb or notify_reads_ydb):
        return False, False

    ydb_repository = _build_ydb_task_repository()
    if render_reads_ydb:
        planner.task_repository = ydb_repository
        planner.task_manager.repository = ydb_repository
        planner.calendar_manager.repository = ydb_repository
        planner.task_calendar_manager.repository = ydb_repository
        print("render_source_switch=applied source=ydb")
    if notify_reads_ydb:
        planner.reminder.task_repository = ydb_repository
        print("notify_source_switch=applied source=ydb")
    return render_reads_ydb, notify_reads_ydb


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

    if mode == "db_migrate":
        client = YdbClient(endpoint=YDB_ENDPOINT, database=YDB_DATABASE)
        ensure_tables(client)
        print("db_migrate_done=true")
        return {
            "mode": "db_migrate",
            "summary": {
                "db_migrate_done": True,
                "ydb_queries_count": client.stats.ydb_queries_count,
                "ydb_duration_ms": client.stats.duration_ms,
                "ydb_error_code": client.stats.error_code,
            },
        }

    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=dry_run,
        mock_external=mock_external,
    )
    source_task_repository = dependencies.task_repository
    planner = GoogleSheetPlanner(
        KEY_JSON,
        SHEET_INFO,
        mode=mode,
        dry_run=dry_run,
        mock_external=mock_external,
        dependencies=dependencies,
    )
    _apply_task_source_switches(planner, mode)

    allow_sync = True
    if MIGRATION_ENABLE_SOURCE_HASH_GATE and mode in {"timer", "test", "sync-only"}:
        rows = []
        for task in source_task_repository.get_all_tasks():
            rows.append(
                {
                    "id": task.id,
                    "brand": task.brand,
                    "format_": task.format_,
                    "project_name": task.project_name,
                    "customer": task.customer,
                    "designer": task.designer,
                    "raw_timing": task.raw_timing,
                    "status": task.status,
                }
            )
        basis = build_hash_basis(rows)
        state_file = Path(MIGRATION_HASH_GATE_STATE_FILE)
        decision = evaluate_hash_gate(source_payload=basis, state_file=state_file)
        print(
            "source_hash_gate="
            f"source_hash={decision.source_hash} "
            f"previous_hash={decision.previous_hash} "
            f"should_sync={decision.should_sync}"
        )
        allow_sync = decision.should_sync
        if decision.should_sync:
            save_last_hash(
                state_file=state_file,
                source_id=SHEET_INFO.spreadsheet_name,
                source_hash=decision.source_hash,
            )

    quality_report = await run_planner_use_case(planner, mode, allow_sync=allow_sync)
    tasks = source_task_repository.get_all_tasks()

    if (
        LEGACY_BLOB_WRITE
        and STORE_MODE in {"dual_write", "ydb_primary", "ydb_only"}
        and mode in {"timer", "test", "sync-only"}
        and allow_sync
    ):
        records = [_task_to_store_record(task) for task in tasks]
        store = build_operational_store(
            STORE_MODE,
            env_name=RUNTIME_ENV,
            ydb_endpoint=YDB_ENDPOINT,
            ydb_database=YDB_DATABASE,
            json_file_path=MIGRATION_STORE_FILE,
        )
        store_result = store.upsert_tasks(records)
        print(
            "migration_store_write="
            f"store_mode={STORE_MODE} "
            "write_path=dual_write_legacy "
            f"store_file={MIGRATION_STORE_FILE} "
            f"records={len(records)} "
            f"result={store_result}"
        )
    elif STORE_MODE in {"dual_write", "ydb_primary", "ydb_only"} and mode in {"timer", "test", "sync-only"}:
        print("migration_store_write=skipped write_path=normalized_only reason=LEGACY_BLOB_WRITE_disabled")

    if STORE_MODE in {"dual_write", "ydb_primary", "ydb_only"} and mode in {"timer", "test", "sync-only"} and allow_sync:
        sync_deferred = False
        readmodel_deferred = False
        source_id = (
            "sheet:"
            f"{source_task_repository.source_sheet_info.spreadsheet_name}:"
            f"{source_task_repository.source_sheet_info.get_sheet_name('tasks')}:A1:Z2000"
        )
        try:
            operational_repo = OperationalTaskRepo(
                endpoint=YDB_ENDPOINT,
                database=YDB_DATABASE,
                ensure_schema=YDB_MIGRATE_ON_START,
            )
            sync_service = YdbSyncService(operational_repo)
            source_values = _read_source_range_values(source_task_repository)
            normalized_tasks = [_task_to_operational_payload(task) for task in tasks]
            sync_result = sync_service.run(
                source_id=source_id,
                source_range_values=source_values,
                normalized_tasks=normalized_tasks,
            )
            _safe_print(
                "migration_operational_sync="
                f"source_id={sync_result.source_id} "
                f"source_hash={sync_result.source_hash} "
                f"previous_hash={sync_result.previous_hash} "
                f"no_changes={sync_result.no_changes} "
                f"tasks_upserted={sync_result.tasks_upserted} "
                f"milestones_upserted={sync_result.milestones_upserted} "
                f"ydb_queries_count={sync_result.ydb_queries_count} "
                f"error_code={sync_result.ydb_error_code}"
            )
        except Exception as exc:
            sync_deferred = True
            safe_error = str(exc).encode("ascii", "backslashreplace").decode("ascii")
            _safe_print(f"migration_ydb_pipeline_error={safe_error}")
            safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
            _safe_print(f"migration_ydb_pipeline_trace={safe_trace}")
        if not sync_deferred:
            try:
                operational_repo = OperationalTaskRepo(
                    endpoint=YDB_ENDPOINT,
                    database=YDB_DATABASE,
                    ensure_schema=False,
                )
                readmodel_repo = FrontendReadmodelRepo(
                    endpoint=YDB_ENDPOINT,
                    database=YDB_DATABASE,
                    ensure_schema=False,
                )
                readmodel_builder = FrontendReadmodelBuilderService(
                    operational_repo=operational_repo,
                    readmodel_repo=readmodel_repo,
                    source_id=source_id,
                    env_name=RUNTIME_ENV,
                    source_sheet_name=source_task_repository.source_sheet_info.spreadsheet_name,
                )
                readmodel_result = readmodel_builder.run(readmodel_id="frontend_v2:default")
                _safe_print(
                    "migration_readmodel_build="
                    f"readmodel_id={readmodel_result.readmodel_id} "
                    f"source_hash={readmodel_result.source_hash} "
                    f"changed={readmodel_result.changed} "
                    f"tasks_count={readmodel_result.tasks_count} "
                    f"ydb_queries_count={readmodel_result.ydb_queries_count}"
                )
            except Exception as exc:
                readmodel_deferred = True
                safe_error = str(exc).encode("ascii", "backslashreplace").decode("ascii")
                _safe_print(f"migration_readmodel_error={safe_error}")
                safe_trace = traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii")
                _safe_print(f"migration_readmodel_trace={safe_trace}")
        print(
            "migration_defer_status "
            f"sync_deferred={sync_deferred} "
            f"readmodel_deferred={readmodel_deferred}"
        )
    _print_quality_report(quality_report)
    return quality_report


if __name__ == "__main__":
    asyncio.run(main())

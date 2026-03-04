"""Основной файл для запуска планировщика задач."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from config import (
    KEY_JSON,
    LEGACY_BLOB_WRITE,
    WRITE_LEGACY_MILESTONES,
    MIGRATION_ENABLE_SOURCE_HASH_GATE,
    MIGRATION_HASH_GATE_STATE_FILE,
    MIGRATION_STORE_FILE,
    YDB_MIGRATE_ON_START,
    YDB_DATABASE,
    YDB_ENDPOINT,
    SHEET_INFO,
)
from src.services.planner_runtime import GoogleSheetPlanner
from src.app.planner_bootstrap import build_planner_dependencies
from src.services.usecases.planner_runtime import resolve_run_mode, run_planner_use_case
from src.app.bootstrap import build_app_context
from src.adapters.store_ydb import build_operational_store
from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo
from src.adapters.ydb.task_repository import YdbOperationalTaskRepository
from src.entrypoints.jobs.db_migrate_job import run_db_migrate
from src.entrypoints.jobs.timer_job import TimerJob
from src.services.pipeline_runtime import run_ydb_sync_readmodel_pipeline
from src.services.sync.hash_basis import build_hash_basis
from src.services.sync.hash_gate import evaluate_hash_gate, save_last_hash
from src.services.source_policy import build_source_policy_matrix

APP_CONTEXT = build_app_context()
PIPELINE_CFG = APP_CONTEXT.cfg.runtime.pipeline
APP_RUNTIME_ENV = APP_CONTEXT.cfg.runtime.runtime.env_default
APP_STORE_MODE = APP_CONTEXT.cfg.runtime.sources.store_mode_default
APP_NOTIFY_SOURCE = APP_CONTEXT.cfg.runtime.sources.notify_source_default
APP_RENDER_SOURCE = APP_CONTEXT.cfg.runtime.sources.render_source_default
APP_TRIGGERS = APP_CONTEXT.cfg.runtime.triggers
TIMER_JOB_SHELL = TimerJob()


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


def _readmodel_freshness_marker(row: object | None) -> dict[str, object]:
    if row is None:
        return {
            "available": False,
            "readmodel_id": "frontend_v2:default",
            "generated_at_utc": None,
            "age_seconds": None,
            "built_from_source_hash": "",
            "payload_hash": "",
        }
    generated_at = getattr(row, "generated_at_utc", None)
    age_seconds = None
    if isinstance(generated_at, datetime):
        age_seconds = int((datetime.now(timezone.utc) - generated_at).total_seconds())
    return {
        "available": True,
        "readmodel_id": getattr(row, "readmodel_id", "frontend_v2:default"),
        "generated_at_utc": generated_at.isoformat() if isinstance(generated_at, datetime) else None,
        "age_seconds": age_seconds,
        "built_from_source_hash": str(getattr(row, "built_from_source_hash", "") or ""),
        "payload_hash": str(getattr(row, "payload_hash", "") or ""),
    }


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
        "task_hash": None,
        "task_revision": 0,
        "raw_payload": task_hash_basis,
        "milestones": milestones,
    }


def _read_source_range_values(source_task_repository, *, worksheet_range: str) -> list[list[str]]:
    spreadsheet_name = source_task_repository.source_sheet_info.spreadsheet_name
    sheet_name = source_task_repository.source_sheet_info.get_sheet_name("tasks")
    return source_task_repository.service.get_worksheet_values(
        spreadsheet_name=spreadsheet_name,
        worksheet_name=sheet_name,
        worksheet_range=worksheet_range,
    )


def _read_source_range_colors(source_task_repository, *, worksheet_range: str) -> list[str]:
    spreadsheet_name = source_task_repository.source_sheet_info.spreadsheet_name
    sheet_name = source_task_repository.source_sheet_info.get_sheet_name("tasks")
    return source_task_repository.service.get_cell_colors(
        spreadsheet_name=spreadsheet_name,
        worksheet_name=sheet_name,
        worksheet_range=worksheet_range,
    )


def _read_source_snapshot(source_task_repository, *, worksheet_range: str) -> dict[str, object]:
    return {
        "range": worksheet_range,
        "values": _read_source_range_values(source_task_repository, worksheet_range=worksheet_range),
        "colors": _read_source_range_colors(source_task_repository, worksheet_range=worksheet_range),
    }


def _build_ydb_task_repository() -> YdbOperationalTaskRepository:
    return YdbOperationalTaskRepository(
        endpoint=YDB_ENDPOINT,
        database=YDB_DATABASE,
    )


def _apply_task_source_switches(planner: GoogleSheetPlanner, mode: str) -> tuple[bool, bool]:
    policy = build_source_policy_matrix(
        readmodel_source="legacy",
        notify_source=APP_NOTIFY_SOURCE,
        render_source=APP_RENDER_SOURCE,
    )
    render_reads_ydb = policy.render_reads_ydb(mode)
    notify_reads_ydb = policy.notify_reads_ydb(mode)
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
    mode = resolve_run_mode(mode=mode, event=event, triggers=APP_TRIGGERS)
    if mode == "timer":
        shell_report = TIMER_JOB_SHELL.run(APP_CONTEXT)
        print(f"timer_job_shell_steps={len(shell_report.get('steps', []))}")
    if mock_external is None:
        mock_external = mode == "test"
    force_refresh = bool(kwargs.get("force_refresh", PIPELINE_CFG.force_refresh_default))
    print(f"{mode=} {dry_run=} {mock_external=}")

    if mode == "db_migrate":
        result = run_db_migrate(endpoint=YDB_ENDPOINT, database=YDB_DATABASE)
        print("db_migrate_done=true")
        return result

    dependencies = build_planner_dependencies(
        KEY_JSON,
        SHEET_INFO,
        dry_run=dry_run,
        mock_external=mock_external,
        cfg=APP_CONTEXT.cfg,
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
    if mode in {"timer", "test", "morning", "reminders-only", "sync-only"} and (
        APP_RENDER_SOURCE == "ydb" or APP_NOTIFY_SOURCE == "ydb"
    ):
        try:
            readmodel_repo = FrontendReadmodelRepo(
                endpoint=YDB_ENDPOINT,
                database=YDB_DATABASE,
                ensure_schema=False,
            )
            marker = _readmodel_freshness_marker(readmodel_repo.get_readmodel("frontend_v2:default"))
            marker["render_source"] = APP_RENDER_SOURCE
            marker["notify_source"] = APP_NOTIFY_SOURCE
            _safe_print(
                "readmodel_freshness="
                + json.dumps(marker, ensure_ascii=False, sort_keys=True)
            )
        except Exception as exc:
            _safe_print(f"readmodel_freshness_error={str(exc)}")

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
        and APP_STORE_MODE in {"dual_write", "ydb_primary", "ydb_only"}
        and mode in {"timer", "test", "sync-only"}
        and allow_sync
    ):
        records = [_task_to_store_record(task) for task in tasks]
        store = build_operational_store(
            APP_STORE_MODE,
            env_name=APP_RUNTIME_ENV,
            ydb_endpoint=YDB_ENDPOINT,
            ydb_database=YDB_DATABASE,
            json_file_path=MIGRATION_STORE_FILE,
        )
        store_result = store.upsert_tasks(records)
        print(
            "migration_store_write="
            f"store_mode={APP_STORE_MODE} "
            "write_path=dual_write_legacy "
            f"store_file={MIGRATION_STORE_FILE} "
            f"records={len(records)} "
            f"result={store_result}"
        )
    elif APP_STORE_MODE in {"dual_write", "ydb_primary", "ydb_only"} and mode in {"timer", "test", "sync-only"}:
        print("migration_store_write=skipped write_path=normalized_only reason=LEGACY_BLOB_WRITE_disabled")

    run_ydb_sync_readmodel_pipeline(
        store_mode=APP_STORE_MODE,
        mode=mode,
        allow_sync=allow_sync,
        tasks=tasks,
        source_task_repository=source_task_repository,
        force_refresh=force_refresh,
        ydb_endpoint=YDB_ENDPOINT,
        ydb_database=YDB_DATABASE,
        ydb_migrate_on_start=YDB_MIGRATE_ON_START,
        write_legacy_milestones=WRITE_LEGACY_MILESTONES,
        runtime_env=APP_RUNTIME_ENV,
        pipeline_cfg=PIPELINE_CFG,
        safe_print=_safe_print,
        read_source_snapshot=_read_source_snapshot,
        task_to_operational_payload=_task_to_operational_payload,
    )
    _print_quality_report(quality_report)
    return quality_report


if __name__ == "__main__":
    asyncio.run(main())


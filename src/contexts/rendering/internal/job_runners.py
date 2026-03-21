from __future__ import annotations

from datetime import timezone
from time import perf_counter

from src.platform.context import AppContext
from src.contexts.rendering.internal.target_guard import RenderTarget, validate_render_target
from src.contexts.rendering.public import (
    get_designers_usecase,
    get_render_job,
    get_request,
    get_snapshot_read_api as _get_rendering_snapshot_read_api,
    get_timeline_usecase,
    get_window,
    get_writer,
)
from src.platform.observability.batching import MetricsBatchCollector, add_flush_metrics


get_snapshot_read_api = _get_rendering_snapshot_read_api


class RenderTimelineJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        collector = MetricsBatchCollector(metrics)
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        started_at = self._ctx.clock()
        wall_clock_started = perf_counter()
        snapshot_read = get_snapshot_read_api(self._ctx)
        usecase = get_timeline_usecase(
            snapshot_read,
            timezone_name=str(self._ctx.cfg.runtime.runtime.timezone or "Europe/Moscow"),
        )
        sheet_info = GoogleSheetInfo(**dict(self._ctx.deps.get("sheet_info", {})))
        source_spreadsheet = str(self._ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
        target_spreadsheet = str(sheet_info.spreadsheet_name or "").strip()
        tasks_sheet_name = str(sheet_info.get_sheet_name("tasks") or "ТАБЛИЧКА").strip()
        target_worksheet = str(sheet_info.get_sheet_name("task_calendar") or "Задачи").strip()
        statuses = list(cmd.payload.get("statuses", ["work", "pre_done"]))
        target_ok, target_warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet=source_spreadsheet,
                target_spreadsheet=target_spreadsheet,
                tasks_sheet_name=tasks_sheet_name,
                target_worksheet=target_worksheet,
            )
        )
        if not target_ok:
            return {
                "artifact": "render_timeline_sheet",
                "status": "blocked",
                "render_applied": False,
                "rows_written": 0,
                "cells_written": 0,
                "target_spreadsheet": target_spreadsheet,
                "target_worksheet": target_worksheet,
                "warnings": list(target_warnings),
                "window": {"start": None, "end": None, "mode": "intersects"},
                "statuses": statuses,
                "selected_tasks": 0,
                "rendered_task_rows": 0,
                "designer_groups": 0,
                "plan_cells_total": 0,
                "plan_borders_total": 0,
                "duration_ms": int((self._ctx.clock() - started_at).total_seconds() * 1000),
                "error": {"code": "render_target_unsafe"},
            }
        writer = get_writer(
            GoogleSheetsService(
                str(self._ctx.deps.get("key_json", "")),
                dry_run=bool(cmd.payload.get("dry_run", False)),
            ),
            spreadsheet_name=sheet_info.spreadsheet_name,
            worksheet_name=target_worksheet,
        )
        request = get_request(
            window=get_window(start=None, end=None, mode="intersects"),
            statuses=statuses,
        )
        result = get_render_job(usecase, writer).run(request)
        warnings = list(result.warnings)
        if not result.applied and not warnings:
            warnings = ["empty_render_plan"]
        labels = {
            "env": str(self._ctx.cfg.runtime.runtime.env_default),
            "module": "render",
            "operation": "timeline",
            "result": "success",
        }
        collector.counter("dtm.render.total", labels=labels)
        collector.timing("dtm.render.duration_ms", float(result.total_duration_ms), labels=labels)
        collector.timing("dtm.render.build_plan_ms", float(result.build_plan_ms), labels=labels)
        collector.timing("dtm.render.write_sheet_ms", float(result.write_sheet_ms), labels=labels)
        collector.gauge("dtm.render.rows_rendered", float(result.rendered_task_rows), labels=labels)
        collector.gauge("dtm.render.cells_written", float(result.cells_written), labels=labels)
        flush_report = collector.flush()
        post_collector = MetricsBatchCollector(metrics)
        add_flush_metrics(
            post_collector,
            env_name=str(self._ctx.cfg.runtime.runtime.env_default),
            module="render",
            operation="timeline",
            report=flush_report,
        )
        render_wall_clock_ms = (perf_counter() - wall_clock_started) * 1000.0
        post_collector.timing("dtm.render.job_wall_clock_ms", render_wall_clock_ms, labels=labels)
        post_collector.flush()
        if logger is not None:
            logger.info(
                "render_finished",
                render_type="timeline",
                target_spreadsheet=str(result.target_spreadsheet),
                target_worksheet=str(result.target_worksheet),
                render_applied=bool(result.applied),
                rows_written=int(result.rows_written),
                cells_written=int(result.cells_written),
                build_plan_ms=float(result.build_plan_ms),
                write_sheet_ms=float(result.write_sheet_ms),
                total_duration_ms=float(result.total_duration_ms),
                wall_clock_ms=round(render_wall_clock_ms, 2),
            )
        return {
            "artifact": "render_timeline_sheet",
            "status": "ok",
            "render_applied": bool(result.applied),
            "rows_written": int(result.rows_written),
            "cells_written": int(result.cells_written),
            "target_spreadsheet": str(result.target_spreadsheet),
            "target_worksheet": str(result.target_worksheet),
            "warnings": warnings,
            "window": {"start": None, "end": None, "mode": "intersects"},
            "statuses": statuses,
            "selected_tasks": int(result.selected_tasks),
            "rendered_task_rows": int(result.rendered_task_rows),
            "designer_groups": int(result.designer_groups),
            "plan_cells_total": int(result.plan_cells_total),
            "plan_borders_total": int(result.plan_borders_total),
            "duration_ms": int((self._ctx.clock() - started_at).total_seconds() * 1000),
            "timings_ms": {
                "build_plan_ms": float(result.build_plan_ms),
                "write_sheet_ms": float(result.write_sheet_ms),
                "total_duration_ms": float(result.total_duration_ms),
            },
            "job_wall_clock_ms": float(round(render_wall_clock_ms, 3)),
            "generated_at": self._ctx.clock().astimezone(timezone.utc).isoformat(),
        }


class RenderDesignersJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        collector = MetricsBatchCollector(metrics)
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        wall_clock_started = perf_counter()
        snapshot_read = get_snapshot_read_api(self._ctx)
        usecase = get_designers_usecase(
            snapshot_read,
            timezone_name=str(self._ctx.cfg.runtime.runtime.timezone or "Europe/Moscow"),
        )
        sheet_info = GoogleSheetInfo(**dict(self._ctx.deps.get("sheet_info", {})))
        source_spreadsheet = str(self._ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
        target_spreadsheet = str(sheet_info.spreadsheet_name or "").strip()
        tasks_sheet_name = str(sheet_info.get_sheet_name("tasks") or "ТАБЛИЧКА").strip()
        target_worksheet = str(sheet_info.get_sheet_name("designers") or "Дизайнеры").strip()
        target_ok, target_warnings = validate_render_target(
            RenderTarget(
                source_spreadsheet=source_spreadsheet,
                target_spreadsheet=target_spreadsheet,
                tasks_sheet_name=tasks_sheet_name,
                target_worksheet=target_worksheet,
            )
        )
        if not target_ok:
            return {
                "artifact": "render_designers_sheet",
                "status": "blocked",
                "render_applied": False,
                "target_spreadsheet": target_spreadsheet,
                "target_worksheet": target_worksheet,
                "warnings": list(target_warnings),
                "error": {"code": "render_target_unsafe"},
            }
        writer = get_writer(
            GoogleSheetsService(
                str(self._ctx.deps.get("key_json", "")),
                dry_run=bool(cmd.payload.get("dry_run", False)),
            ),
            spreadsheet_name=sheet_info.spreadsheet_name,
            worksheet_name=target_worksheet,
        )
        result = get_render_job(usecase, writer).run(
            get_request(
                window=get_window(start=None, end=None, mode="intersects"),
                statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
            )
        )
        labels = {
            "env": str(self._ctx.cfg.runtime.runtime.env_default),
            "module": "render",
            "operation": "designers",
            "result": "success",
        }
        collector.counter("dtm.render.total", labels=labels)
        collector.timing("dtm.render.duration_ms", float(result.total_duration_ms), labels=labels)
        collector.timing("dtm.render.build_plan_ms", float(result.build_plan_ms), labels=labels)
        collector.timing("dtm.render.write_sheet_ms", float(result.write_sheet_ms), labels=labels)
        flush_report = collector.flush()
        post_collector = MetricsBatchCollector(metrics)
        add_flush_metrics(
            post_collector,
            env_name=str(self._ctx.cfg.runtime.runtime.env_default),
            module="render",
            operation="designers",
            report=flush_report,
        )
        render_wall_clock_ms = (perf_counter() - wall_clock_started) * 1000.0
        post_collector.timing("dtm.render.job_wall_clock_ms", render_wall_clock_ms, labels=labels)
        post_collector.flush()
        if logger is not None:
            logger.info(
                "render_finished",
                render_type="designers",
                target_spreadsheet=str(result.target_spreadsheet),
                target_worksheet=str(result.target_worksheet),
                render_applied=bool(result.applied),
                rows_written=int(result.rows_written),
                cells_written=int(result.cells_written),
                build_plan_ms=float(result.build_plan_ms),
                write_sheet_ms=float(result.write_sheet_ms),
                total_duration_ms=float(result.total_duration_ms),
                wall_clock_ms=round(render_wall_clock_ms, 2),
            )
        return {
            "artifact": "render_designers_sheet",
            "status": "ok",
            "render_applied": bool(result.applied),
            "rows_written": int(result.rows_written),
            "cells_written": int(result.cells_written),
            "target_spreadsheet": str(result.target_spreadsheet),
            "target_worksheet": str(result.target_worksheet),
            "warnings": list(result.warnings),
            "timings_ms": {
                "build_plan_ms": float(result.build_plan_ms),
                "write_sheet_ms": float(result.write_sheet_ms),
                "total_duration_ms": float(result.total_duration_ms),
            },
            "job_wall_clock_ms": float(round(render_wall_clock_ms, 3)),
        }


__all__ = ["RenderDesignersJob", "RenderTimelineJob"]

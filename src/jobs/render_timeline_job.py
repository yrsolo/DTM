from __future__ import annotations

from datetime import timezone

from src.app.context import AppContext
from src.observability import timed
from src.render import GoogleSheetsPlanWriter, RenderJob, RenderRequest, RenderUseCase, SheetTarget
from src.render.target_guard import RenderTarget, validate_render_target
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import Window


class RenderTimelineJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        started_at = self._ctx.clock()
        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = RenderUseCase(
            snapshot_engine,
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
        writer = GoogleSheetsPlanWriter(
            GoogleSheetsService(str(self._ctx.deps.get("key_json", "")), dry_run=bool(cmd.payload.get("dry_run", False))),
            SheetTarget(spreadsheet_name=sheet_info.spreadsheet_name, worksheet_name=target_worksheet),
        )
        request = RenderRequest(
            window=Window(start=None, end=None, mode="intersects"),
            statuses=statuses,
        )
        with timed(metrics, "dtm.render.duration_ms", {"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "render", "operation": "timeline", "result": "finished"}):
            result = RenderJob(usecase, writer).run(request)
        warnings = list(result.warnings)
        if not result.applied and not warnings:
            warnings = ["empty_render_plan"]
        if metrics is not None:
            metrics.counter("dtm.render.total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "render", "operation": "timeline", "result": "success"})
            metrics.gauge("dtm.render.rows_rendered", float(result.rendered_task_rows), labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "render", "operation": "timeline", "result": "success"})
            metrics.gauge("dtm.render.cells_written", float(result.cells_written), labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "render", "operation": "timeline", "result": "success"})
        if logger is not None:
            logger.info(
                "render_finished",
                render_type="timeline",
                target_spreadsheet=str(result.target_spreadsheet),
                target_worksheet=str(result.target_worksheet),
                render_applied=bool(result.applied),
                rows_written=int(result.rows_written),
                cells_written=int(result.cells_written),
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
            "generated_at": self._ctx.clock().astimezone(timezone.utc).isoformat(),
        }

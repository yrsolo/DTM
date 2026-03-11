from __future__ import annotations

from src.app.context import AppContext
from src.observability import emit_last_and_avg5_gauges, extract_recent_success_values
from src.render import DesignersRenderUseCase, GoogleSheetsPlanWriter, RenderJob, RenderRequest, SheetTarget
from src.render.target_guard import RenderTarget, validate_render_target
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import Window


class RenderDesignersJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        from utils.service import GoogleSheetInfo, GoogleSheetsService

        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = DesignersRenderUseCase(
            snapshot_engine,
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
        writer = GoogleSheetsPlanWriter(
            GoogleSheetsService(str(self._ctx.deps.get("key_json", "")), dry_run=bool(cmd.payload.get("dry_run", False))),
            SheetTarget(spreadsheet_name=sheet_info.spreadsheet_name, worksheet_name=target_worksheet),
        )
        result = RenderJob(usecase, writer).run(
            RenderRequest(
                window=Window(start=None, end=None, mode="intersects"),
                statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
            )
        )
        if metrics is not None:
            labels = {"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "render", "operation": "designers", "result": "success"}
            metrics.counter("dtm.render.total", labels=labels)
            metrics.timing("dtm.render.duration_ms", float(result.total_duration_ms), labels=labels)
            metrics.timing("dtm.render.build_plan_ms", float(result.build_plan_ms), labels=labels)
            metrics.timing("dtm.render.write_sheet_ms", float(result.write_sheet_ms), labels=labels)
            status_store = self._ctx.deps.get("job_status_store")
            recent_records = status_store.get_recent_by_command("render_designers_sheet", limit=10) if status_store is not None else []
            for logical_name, timing_key in {
                "build_plan": "build_plan_ms",
                "write_sheet": "write_sheet_ms",
                "duration": "total_duration_ms",
            }.items():
                previous_values = extract_recent_success_values(recent_records, timing_key=timing_key, limit=4)
                emit_last_and_avg5_gauges(
                    metrics,
                    metric_prefix="dtm.render",
                    logical_name=logical_name,
                    current_value_ms=result.build_plan_ms if timing_key == "build_plan_ms" else (
                        result.write_sheet_ms if timing_key == "write_sheet_ms" else result.total_duration_ms
                    ),
                    previous_values_ms=previous_values,
                    labels=labels,
                )
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
        }

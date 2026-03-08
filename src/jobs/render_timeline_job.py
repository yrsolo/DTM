from __future__ import annotations

from src.app.context import AppContext
from src.render import GoogleSheetsPlanWriter, RenderJob, RenderRequest, RenderUseCase, SheetTarget
from src.render.target_guard import RenderTarget, validate_render_target
from src.snapshot_engine import build_snapshot_engine
from src.snapshot_engine.model import Window
from utils.service import GoogleSheetInfo, GoogleSheetsService


class RenderTimelineJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = RenderUseCase(snapshot_engine)
        sheet_info = GoogleSheetInfo(**dict(self._ctx.deps.get("sheet_info", {})))
        source_spreadsheet = str(self._ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
        target_spreadsheet = str(sheet_info.spreadsheet_name or "").strip()
        tasks_sheet_name = str(sheet_info.get_sheet_name("tasks") or "ТАБЛИЧКА").strip()
        target_worksheet = str(sheet_info.get_sheet_name("task_calendar") or "Задачи").strip()
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
        return {
            "artifact": "render_timeline_sheet",
            "status": "ok",
            "render_applied": bool(result.applied),
            "rows_written": int(result.rows_written),
            "cells_written": int(result.cells_written),
            "target_spreadsheet": str(result.target_spreadsheet),
            "target_worksheet": str(result.target_worksheet),
            "warnings": list(result.warnings),
        }

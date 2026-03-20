"""Platform-owned render runtime orchestration."""

from __future__ import annotations

from time import perf_counter
from types import SimpleNamespace
from typing import Any

from src.contexts.rendering.internal.job_runners import RenderDesignersJob, RenderTimelineJob


def _default_statuses(statuses: list[str] | None) -> list[str]:
    return list(statuses or ["work", "pre_done"])


def _build_render_cmd(*, dry_run: bool, statuses: list[str]) -> Any:
    return SimpleNamespace(payload={"dry_run": bool(dry_run), "statuses": list(statuses)})


def _build_blocked_payload(
    *,
    ctx: Any,
    result: dict[str, Any],
    mode: str,
    started_at: float,
) -> dict[str, Any]:
    target_spreadsheet = str(result.get("target_spreadsheet", ""))
    target_worksheet = str(result.get("target_worksheet", ""))
    source_spreadsheet = str(ctx.cfg.tables.google_sheets.get("source_sheet_name_default", "")).strip()
    tasks_sheet_name = str(ctx.deps.get("sheet_info", {}).get("tasks_sheet_name") or "ТАБЛИЧКА").strip()
    return {
        "artifact": "render_v2",
        "status": "blocked",
        "mode": str(mode),
        "render_applied": False,
        "rows_written": 0,
        "cells_written": 0,
        "target_spreadsheet": target_spreadsheet,
        "target_worksheet": target_worksheet,
        "warnings": list(result.get("warnings", [])),
        "error": {
            "code": "render_target_unsafe",
            "details": {
                "source_spreadsheet": source_spreadsheet,
                "target_spreadsheet": target_spreadsheet,
                "target_worksheet": target_worksheet,
                "tasks_sheet_name": tasks_sheet_name,
            },
        },
        "duration_ms": int((perf_counter() - started_at) * 1000),
        "summary": {"task_row_issue_count": 0},
    }


def run_render_runtime(
    ctx: Any,
    *,
    mode: str,
    force_refresh: bool,
    dry_run: bool,
    statuses: list[str] | None = None,
) -> dict[str, Any]:
    """Execute the render_v2 runtime flow using canonical per-sheet jobs."""

    normalized_statuses = _default_statuses(statuses)
    started_at = perf_counter()
    cmd = _build_render_cmd(dry_run=dry_run, statuses=normalized_statuses)

    timeline_result = RenderTimelineJob(ctx).run(cmd)
    if str(timeline_result.get("status", "")).strip().lower() == "blocked":
        return _build_blocked_payload(
            ctx=ctx,
            result=timeline_result,
            mode=mode,
            started_at=started_at,
        )

    designers_result = RenderDesignersJob(ctx).run(cmd)
    if str(designers_result.get("status", "")).strip().lower() == "blocked":
        return _build_blocked_payload(
            ctx=ctx,
            result=designers_result,
            mode=mode,
            started_at=started_at,
        )

    return {
        "artifact": "render_v2",
        "status": "ok",
        "mode": str(mode),
        "force_refresh": bool(force_refresh),
        "render_applied": bool(
            timeline_result.get("render_applied") or designers_result.get("render_applied")
        ),
        "rows_written": int(timeline_result.get("rows_written", 0))
        + int(designers_result.get("rows_written", 0)),
        "cells_written": int(timeline_result.get("cells_written", 0))
        + int(designers_result.get("cells_written", 0)),
        "target_spreadsheet": str(timeline_result.get("target_spreadsheet", "")),
        "target_worksheet": "Задачи,Дизайнеры",
        "targets": {
            "task_calendar": {
                "target_worksheet": str(timeline_result.get("target_worksheet", "")),
                "render_applied": bool(timeline_result.get("render_applied")),
                "rows_written": int(timeline_result.get("rows_written", 0)),
                "cells_written": int(timeline_result.get("cells_written", 0)),
                "warnings": list(timeline_result.get("warnings", [])),
            },
            "designers": {
                "target_worksheet": str(designers_result.get("target_worksheet", "")),
                "render_applied": bool(designers_result.get("render_applied")),
                "rows_written": int(designers_result.get("rows_written", 0)),
                "cells_written": int(designers_result.get("cells_written", 0)),
                "warnings": list(designers_result.get("warnings", [])),
            },
        },
        "warnings": list(timeline_result.get("warnings", [])) + list(designers_result.get("warnings", [])),
        "duration_ms": int((perf_counter() - started_at) * 1000),
        "summary": {"task_row_issue_count": 0},
    }

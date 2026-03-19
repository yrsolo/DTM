"""Shared runtime entry for planner modes used by jobs and HTTP entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.reminders.public import (
    get_enhancer as _get_reminders_enhancer,
    get_formatter as _get_reminders_formatter,
    get_job_runner as _get_reminder_job_runner,
    get_sender as _get_reminders_sender,
    get_usecase as _get_reminders_usecase,
)
from src.contexts.snapshot.public import get_snapshot_engine as _get_snapshot_engine
from src.entrypoints.jobs.quality_report_job import print_quality_report as _print_quality_report
from src.entrypoints.jobs.runtime_context_job import RuntimeContextRequest, resolve_runtime_context
from src.entrypoints.jobs.timer_job import TimerJob
from src.entrypoints.runtime.runtime_contract import STANDARD_RUN_MODES, is_legacy_mode
from src.notify import ReminderJob, ReminderRequest
from src.platform.app_context import build_runtime_app_context
from src.platform.runtime.render_runtime import run_render_runtime
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
from src.services.timer_pipeline import RunRequest as TimerRunRequest
from src.services.timer_pipeline import TimerPipeline


build_snapshot_engine = _get_snapshot_engine
ReminderJob = ReminderJob


def _resolve_standard_run_mode(
    mode: str | None = None,
    event: Any = None,
    triggers: dict[str, str] | None = None,
) -> str:
    if mode:
        return str(mode).strip().lower()
    if event == "morning":
        return "morning"
    if isinstance(event, dict):
        try:
            trigger_id = str(event["messages"][0]["details"]["trigger_id"]).strip()
        except (TypeError, KeyError, IndexError):
            trigger_id = ""
        if trigger_id:
            return str((triggers or {}).get(trigger_id, "test")).strip().lower()
    return "test"


def _build_notify_enhancer(*, ctx: Any, mock_external: bool):
    return _get_reminders_enhancer(ctx, mock_external=mock_external)


async def _run_reminder_mode(
    *,
    app_context: Any,
    cfg: Any,
    deps: dict[str, Any],
    normalized_mode: str,
    mock_external: bool,
    runtime_env: str,
):
    """Execute reminder-oriented runtime modes through the reminders context."""

    snapshot_engine = build_snapshot_engine(app_context)
    usecase = _get_reminders_usecase(snapshot_engine)
    formatter = _get_reminders_formatter(app_context)
    sender = _get_reminders_sender(app_context)
    notify_cfg = cfg.runtime.notify
    llm_mode = str(notify_cfg.llm_mode_default or "provider")
    mock_llm = bool(mock_external or llm_mode == "draft_only" or runtime_env == "test")
    enhancer = _build_notify_enhancer(ctx=app_context, mock_external=mock_llm)
    reminder_result = await _get_reminder_job_runner(
        usecase=usecase,
        formatter=formatter,
        sender=sender,
        helper_character=str(cfg.llm.assistant.get("helper_character", "")),
        enhancer=enhancer,
        people_lookup=snapshot_engine,
        default_chat_id=str(deps.get("default_chat_id", "")).strip(),
        enhance_concurrency=int(notify_cfg.enhance_concurrency),
        send_retry_attempts=int(notify_cfg.send_retry_attempts),
        send_retry_backoff_seconds=float(notify_cfg.send_retry_backoff_seconds),
        send_retry_backoff_multiplier=float(notify_cfg.send_retry_backoff_multiplier),
        llm_mode=llm_mode,
        llm_model=str(cfg.llm.models.get("openai_default", "")),
        runtime_env=runtime_env,
        mock_llm=mock_llm,
    ).run(
        ReminderRequest(
            mode=normalized_mode,
            statuses=["work", "pre_done"],
            include_today=True,
            include_next_workday=True,
            force_test_chat=(runtime_env == "test" or normalized_mode == "test"),
            test_chat_id_override=str(notify_cfg.test_chat_id_override or ""),
        )
    )
    if normalized_mode in {"reminder_v2", "reminders-only", "morning"}:
        return {
            "artifact": reminder_result.artifact,
            "status": reminder_result.status,
            "mode": reminder_result.mode,
            "summary": {
                "task_row_issue_count": 0,
                "groups": len(reminder_result.groups),
            },
            "delivery_counters": dict(reminder_result.delivery_counters),
            "enhancement_counters": dict(reminder_result.enhancement_counters),
            "warnings": list(reminder_result.warnings),
            "today": reminder_result.today,
            "next_workday": reminder_result.next_workday,
        }
    return None


@dataclass(frozen=True)
class PlannerRuntimeRequest:
    event: Any = None
    mode: str | None = None
    dry_run: bool = False
    mock_external: Any = None
    force_refresh: bool | None = None
    app_context: Any = None


async def run_planner_runtime(request: PlannerRuntimeRequest):
    """Run planner runtime mode through shared entry logic."""

    app_context = request.app_context or build_runtime_app_context()
    deps = app_context.deps
    cfg = app_context.cfg
    pipeline_cfg = cfg.runtime.pipeline
    runtime_env = cfg.runtime.runtime.env_default
    triggers = dict(cfg.runtime.triggers)
    key_json = str(deps.get("key_json", ""))
    sheet_info = dict(deps.get("sheet_info", {}))
    timer_job_shell = TimerJob()
    dry_run = request.dry_run

    runtime_ctx = resolve_runtime_context(
        RuntimeContextRequest(
            mode=request.mode,
            event=request.event,
            dry_run=dry_run,
            mock_external=request.mock_external,
            force_refresh_raw=request.force_refresh,
            triggers=triggers,
            force_refresh_default=pipeline_cfg.force_refresh_default,
            resolve_run_mode=_resolve_standard_run_mode,
            timer_job_shell=timer_job_shell,
            app_context=app_context,
        )
    )
    mode = runtime_ctx.mode
    mock_external = runtime_ctx.mock_external
    force_refresh = runtime_ctx.force_refresh

    task_source = build_sheets_normalized_task_source(
        key_json=key_json,
        sheet_info_data=sheet_info,
        cfg=cfg,
        dry_run=dry_run,
    )
    normalized_mode = str(mode).strip().lower()
    if is_legacy_mode(normalized_mode) or normalized_mode not in STANDARD_RUN_MODES:
        return {
            "artifact": "dtm_runtime",
            "status": "unsupported_mode",
            "mode": normalized_mode,
            "supported_modes": sorted(STANDARD_RUN_MODES),
        }
    quality_report: dict[str, Any] = {"summary": {"task_row_issue_count": 0}}

    if normalized_mode in {"reminder_v2", "reminders-only", "morning", "test"}:
        reminder_payload = await _run_reminder_mode(
            app_context=app_context,
            cfg=cfg,
            deps=deps,
            normalized_mode=normalized_mode,
            mock_external=mock_external,
            runtime_env=runtime_env,
        )
        if reminder_payload is not None:
            return reminder_payload

    TimerPipeline(app_context).run(
        TimerRunRequest(
            mode=mode,
            force_refresh=force_refresh,
            task_source=task_source,
        )
    )

    if normalized_mode == "render_v2":
        return run_render_runtime(
            app_context,
            mode="render_v2",
            force_refresh=bool(force_refresh),
            dry_run=dry_run,
            statuses=["work", "pre_done"],
        )

    _print_quality_report(quality_report)
    return quality_report

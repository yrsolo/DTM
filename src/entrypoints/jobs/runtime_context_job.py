"""Runtime context preparation helper for main job flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class RuntimeContext:
    mode: str
    mock_external: bool
    force_refresh: bool


@dataclass(slots=True)
class RuntimeContextRequest:
    mode: str | None
    event: Any
    dry_run: bool
    mock_external: bool | None
    force_refresh_raw: Any
    triggers: list[str]
    force_refresh_default: bool
    resolve_run_mode: Callable[..., str]
    timer_job_shell: Any
    app_context: Any


def resolve_runtime_context(
    request: RuntimeContextRequest,
) -> RuntimeContext:
    resolved_mode = request.resolve_run_mode(
        mode=request.mode,
        event=request.event,
        triggers=request.triggers,
    )
    if resolved_mode == "timer":
        shell_report = request.timer_job_shell.run(request.app_context)
        print(f"timer_job_shell_steps={len(shell_report.get('steps', []))}")

    resolved_mock_external = (
        (resolved_mode == "test") if request.mock_external is None else bool(request.mock_external)
    )
    force_refresh = bool(
        request.force_refresh_raw
        if request.force_refresh_raw is not None
        else request.force_refresh_default
    )
    mode = resolved_mode
    mock_external = resolved_mock_external
    print(f"{mode=} {request.dry_run=} {mock_external=}")
    return RuntimeContext(
        mode=resolved_mode,
        mock_external=resolved_mock_external,
        force_refresh=force_refresh,
    )

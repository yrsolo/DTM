"""Runtime context preparation helper for main job flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class RuntimeContext:
    mode: str
    mock_external: bool
    force_refresh: bool


def resolve_runtime_context(
    *,
    mode: str | None,
    event: Any,
    dry_run: bool,
    mock_external: bool | None,
    force_refresh_raw: Any,
    triggers: list[str],
    force_refresh_default: bool,
    resolve_run_mode: Callable[..., str],
    timer_job_shell: Any,
    app_context: Any,
) -> RuntimeContext:
    resolved_mode = resolve_run_mode(mode=mode, event=event, triggers=triggers)
    if resolved_mode == "timer":
        shell_report = timer_job_shell.run(app_context)
        print(f"timer_job_shell_steps={len(shell_report.get('steps', []))}")

    resolved_mock_external = (resolved_mode == "test") if mock_external is None else bool(mock_external)
    force_refresh = bool(force_refresh_raw if force_refresh_raw is not None else force_refresh_default)
    mode = resolved_mode
    mock_external = resolved_mock_external
    print(f"{mode=} {dry_run=} {mock_external=}")
    return RuntimeContext(
        mode=resolved_mode,
        mock_external=resolved_mock_external,
        force_refresh=force_refresh,
    )

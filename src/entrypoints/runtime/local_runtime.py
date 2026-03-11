"""Thin local runtime adapter for developer tooling."""

from __future__ import annotations

from typing import Any

from src.entrypoints.runtime.planner_runtime_entry import PlannerRuntimeRequest, run_planner_runtime


async def run_local_runtime(
    *,
    event: Any = None,
    mode: str | None = None,
    dry_run: bool = False,
    mock_external: Any = None,
    force_refresh: bool | None = None,
):
    """Build the standard runtime request and execute it locally."""
    return await run_planner_runtime(
        PlannerRuntimeRequest(
            event=event,
            mode=mode,
            dry_run=dry_run,
            mock_external=mock_external,
            force_refresh=force_refresh,
        )
    )

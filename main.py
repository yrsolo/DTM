"""Основной entrypoint запуска planner runtime."""

import asyncio

from typing import Any

from src.entrypoints.runtime.planner_runtime_entry import PlannerRuntimeRequest, run_planner_runtime


async def main(
    request: PlannerRuntimeRequest | None = None,
    *,
    event: Any = None,
    mode: str | None = None,
    dry_run: bool = False,
    mock_external: Any = None,
    force_refresh: bool | None = None,
):
    """Тонкий wrapper поверх shared runtime entry."""
    runtime_request = request or PlannerRuntimeRequest(
        event=event,
        mode=mode,
        dry_run=dry_run,
        mock_external=mock_external,
        force_refresh=force_refresh,
    )
    return await run_planner_runtime(runtime_request)


if __name__ == "__main__":
    asyncio.run(main())

"""Основной entrypoint запуска planner runtime."""

import asyncio

from src.entrypoints.runtime.planner_runtime_entry import run_planner_runtime


async def main(**kwargs):
    """Тонкий wrapper поверх shared runtime entry."""
    return await run_planner_runtime(**kwargs)


if __name__ == "__main__":
    asyncio.run(main())

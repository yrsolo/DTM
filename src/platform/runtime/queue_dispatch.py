"""Target explicit queue dispatch skeleton."""

from __future__ import annotations

from typing import Any


async def dispatch_command(command_type: str, _command: Any) -> dict[str, Any]:
    """Explicit command routing placeholder for the target platform layer."""

    match str(command_type or "").strip():
        case _:
            return {
                "artifact": "queue_dispatch",
                "status": "unsupported",
                "command_type": str(command_type or ""),
            }


"""Application runtime context primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import sys
from typing import Any, Callable

from src.config.schema import AppConfig


def utc_now() -> datetime:
    """Default clock callable for runtime context."""

    return datetime.now(timezone.utc)


def default_logger(message: str) -> None:
    """Default logger callable for runtime context."""
    text = str(message)
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe = text.encode(encoding, "backslashreplace").decode(encoding, "ignore")
        print(safe)


@dataclass(slots=True)
class AppContext:
    """Shared runtime context: config + dependencies + infra callables."""

    cfg: AppConfig
    deps: dict[str, Any] = field(default_factory=dict)
    clock: Callable[[], datetime] = utc_now
    log: Callable[[str], None] = default_logger

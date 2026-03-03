"""Application bootstrap for config-first runtime wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config.loader import load_config
from src.config.schema import AppConfig


@dataclass(slots=True)
class AppContext:
    """Shared runtime context (phase-0 scaffold)."""

    cfg: AppConfig
    deps: dict[str, Any]


def build_app_context() -> AppContext:
    """Load YAML config and return bootstrap context.

    Dependency wiring is intentionally lightweight in CAM-CONFIG-REFORM-V0.
    Full service/repository composition is planned for subsequent campaigns.
    """

    cfg = load_config()
    return AppContext(cfg=cfg, deps={})

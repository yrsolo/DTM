"""Application bootstrap for config-first runtime wiring."""

from __future__ import annotations

from src.app.context import AppContext
from src.config.loader import load_config


def build_app_context() -> AppContext:
    """Load YAML config and return bootstrap context.

    Dependency wiring is intentionally lightweight in CAM-CONFIG-REFORM-V0.
    Full service/repository composition is planned for subsequent campaigns.
    """

    cfg = load_config()
    return AppContext(cfg=cfg, deps={})

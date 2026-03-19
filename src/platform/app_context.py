"""Platform boundary for building runtime app contexts."""

from __future__ import annotations

from src.app.bootstrap import build_app_context


def build_runtime_app_context():
    """Build a fresh app context through the platform boundary."""

    return build_app_context()

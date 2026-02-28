"""Smoke check for Stage 8 static web prototype assets."""

from __future__ import annotations

from pathlib import Path

STATIC_ROOT = Path("web_prototype") / "static"
REQUIRED_ASSETS = ("index.html", "app.js", "styles.css")
INDEX_MARKERS = ("timelineView", "designerView", "taskDetailsView", "loadFixtureBtn")
APP_MARKERS = ("renderTimeline", "renderDesignerBoard", "renderTaskDetails", "applyFilters")


def _require_markers(content: str, markers: tuple[str, ...], error_prefix: str) -> None:
    """Ensure all required markers are present in static asset content."""

    for marker in markers:
        if marker not in content:
            raise SystemExit(f"{error_prefix}:{marker}")


def main() -> int:
    """Validate required static assets and frontend marker hooks."""

    asset_paths = [STATIC_ROOT / filename for filename in REQUIRED_ASSETS]
    for path in asset_paths:
        if not path.exists():
            raise SystemExit(f"missing_asset:{path}")

    index_file = STATIC_ROOT / "index.html"
    app_file = STATIC_ROOT / "app.js"

    index = index_file.read_text(encoding="utf-8")
    _require_markers(index, INDEX_MARKERS, "missing_index_marker")

    app = app_file.read_text(encoding="utf-8")
    _require_markers(app, APP_MARKERS, "missing_app_marker")

    print("web_prototype_assets_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


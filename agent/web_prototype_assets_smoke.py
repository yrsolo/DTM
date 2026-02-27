"""Smoke check for Stage 8 static web prototype assets."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path("web_prototype") / "static"
    index_file = root / "index.html"
    app_file = root / "app.js"
    css_file = root / "styles.css"

    for path in (index_file, app_file, css_file):
        if not path.exists():
            raise SystemExit(f"missing_asset:{path}")

    index = index_file.read_text(encoding="utf-8")
    for marker in ("timelineView", "designerView", "taskDetailsView", "loadFixtureBtn"):
        if marker not in index:
            raise SystemExit(f"missing_index_marker:{marker}")

    app = app_file.read_text(encoding="utf-8")
    for marker in ("renderTimeline", "renderDesignerBoard", "renderTaskDetails", "applyFilters"):
        if marker not in app:
            raise SystemExit(f"missing_app_marker:{marker}")

    print("web_prototype_assets_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


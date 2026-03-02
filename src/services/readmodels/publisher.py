"""Read-model publication helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def publish_read_model_to_file(payload: dict[str, Any], file_path: str | Path) -> Path:
    """Persist read-model payload to JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


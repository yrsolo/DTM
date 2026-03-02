"""Read-model build handler."""

from __future__ import annotations

from typing import Any

from src.services.readmodels import build_read_models, publish_read_model_to_file

def handle_build_readmodels(event: dict[str, Any]) -> dict[str, Any]:
    """Build read models from provided normalized task payload.

    Event fields:
    - `normalized_tasks`: list[dict]
    - `output_file`: optional output json file path
    """
    tasks = event.get("normalized_tasks", [])
    payload = build_read_models(tasks)

    output_file = str(event.get("output_file", "")).strip()
    if output_file:
        published_to = str(publish_read_model_to_file(payload, output_file))
    else:
        published_to = ""

    return {
        "status": "ok",
        "handler": "build_readmodels",
        "tasks_input": len(tasks),
        "published_to": published_to,
        "artifact": payload.get("artifact"),
    }

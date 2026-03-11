from __future__ import annotations

import json
from datetime import datetime, timezone

from .model import Command, RequestedBy


def _format_datetime(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("created_at_utc is required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def command_to_json(cmd: Command) -> str:
    payload = {
        "job_id": str(cmd.job_id).strip(),
        "type": str(cmd.type).strip(),
        "created_at_utc": _format_datetime(cmd.created_at_utc),
        "requested_by": {
            "source": str(cmd.requested_by.source).strip(),
            "user_id": cmd.requested_by.user_id,
            "chat_id": cmd.requested_by.chat_id,
        },
        "payload": dict(cmd.payload or {}),
        "idempotency_key": cmd.idempotency_key,
    }
    if not payload["job_id"]:
        raise ValueError("job_id is required")
    if not payload["type"]:
        raise ValueError("type is required")
    if not payload["requested_by"]["source"]:
        raise ValueError("requested_by.source is required")
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def command_from_json(s: str) -> Command:
    parsed = json.loads(str(s or "").strip() or "{}")
    if not isinstance(parsed, dict):
        raise ValueError("Command payload must be an object")
    requested_by = parsed.get("requested_by")
    if not isinstance(requested_by, dict):
        raise ValueError("requested_by object is required")
    payload = parsed.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    return Command(
        job_id=str(parsed.get("job_id", "")).strip(),
        type=str(parsed.get("type", "")).strip(),
        created_at_utc=_parse_datetime(str(parsed.get("created_at_utc", "")).strip()),
        requested_by=RequestedBy(
            source=str(requested_by.get("source", "")).strip(),
            user_id=str(requested_by.get("user_id", "")).strip() or None,
            chat_id=str(requested_by.get("chat_id", "")).strip() or None,
        ),
        payload=dict(payload),
        idempotency_key=str(parsed.get("idempotency_key", "")).strip() or None,
    )

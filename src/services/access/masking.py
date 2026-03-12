"""Deterministic masking for browser-facing frontend payloads."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Any

from src.entrypoints.http.access_context import AccessContext


def _stable_token(kind: str, raw: str, *, version: str) -> str:
    payload = f"{version}:{kind}:{raw}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:8]


def _mask_value(kind: str, raw: str, *, version: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return value
    token = _stable_token(kind, value, version=version)
    if kind == "person":
        return f"Designer-{token}"
    if kind == "group":
        return f"Project-{token}"
    if kind == "title":
        return f"Task-{token}"
    if kind == "brand":
        return f"Brand-{token}"
    if kind == "customer":
        return f"Customer-{token}"
    if kind == "filename":
        return f"file-{token}"
    if kind == "preview":
        return f"preview-{token}"
    return f"masked-{token}"


def _apply_mask(payload: dict[str, Any], *, version: str) -> dict[str, Any]:
    masked = json.loads(json.dumps(payload, ensure_ascii=False))
    filters = dict(masked.get("filters", {}) or {})
    if str(filters.get("designer") or "").strip():
        filters["designer"] = _mask_value("person", str(filters.get("designer") or ""), version=version)
    masked["filters"] = filters

    entities = dict(masked.get("entities", {}) or {})
    people = []
    for item in list(entities.get("people", []) or []):
        row = dict(item or {})
        row["name"] = _mask_value("person", str(row.get("name") or ""), version=version)
        people.append(row)
    groups = []
    for item in list(entities.get("groups", []) or []):
        row = dict(item or {})
        row["name"] = _mask_value("group", str(row.get("name") or ""), version=version)
        groups.append(row)
    entities["people"] = people
    entities["groups"] = groups
    masked["entities"] = entities

    tasks = []
    for item in list(masked.get("tasks", []) or []):
        row = dict(item or {})
        row["title"] = _mask_value("title", str(row.get("title") or ""), version=version)
        row["brand"] = _mask_value("brand", str(row.get("brand") or ""), version=version)
        row["customer"] = _mask_value("customer", str(row.get("customer") or ""), version=version)
        row["history"] = _mask_value("text", str(row.get("history") or ""), version=version)
        attachments = []
        for attachment in list(row.get("attachments", []) or []):
            masked_attachment = dict(attachment or {})
            masked_attachment["filename"] = _mask_value(
                "filename", str(masked_attachment.get("filename") or ""), version=version
            )
            masked_attachment["uploadedBy"] = _mask_value(
                "person", str(masked_attachment.get("uploadedBy") or ""), version=version
            )
            masked_attachment["preview"] = _mask_value(
                "preview", str(masked_attachment.get("preview") or ""), version=version
            )
            attachments.append(masked_attachment)
        row["attachments"] = attachments
        tasks.append(row)
    masked["tasks"] = tasks
    return masked


def mask_frontend_payload(
    payload: dict[str, Any],
    access: AccessContext,
    *,
    dictionary_version: str,
    metrics_client: Any = None,
    metrics_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not access.masked:
        return dict(payload)
    started = perf_counter()
    masked = _apply_mask(payload, version=str(dictionary_version or "v1").strip() or "v1")
    if metrics_client is not None:
        metrics_client.timing("dtm.api.masking_ms", (perf_counter() - started) * 1000.0, labels=dict(metrics_labels or {}))
    return masked

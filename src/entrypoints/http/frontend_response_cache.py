"""Helpers for exact default frontend response cache."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from src.entrypoints.http.access_context import AccessContext
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.event_parser import normalize_path


DEFAULT_FRONTEND_CACHE_STATUSES = ("work", "pre_done", "done", "wait")
DEFAULT_FRONTEND_CACHE_LIMIT = 60
DEFAULT_FRONTEND_CACHE_INCLUDE_PEOPLE = True
DEFAULT_FRONTEND_CACHE_QUERY_ID = "frontend_v2_default_v1"


def is_default_frontend_cache_query(
    *,
    statuses: list[str],
    designer: str,
    limit: int,
    include_people: bool,
    window_data: dict[str, Any],
) -> bool:
    return (
        tuple(str(item or "").strip() for item in list(statuses or [])) == DEFAULT_FRONTEND_CACHE_STATUSES
        and not str(designer or "").strip()
        and int(limit) == DEFAULT_FRONTEND_CACHE_LIMIT
        and bool(include_people) is DEFAULT_FRONTEND_CACHE_INCLUDE_PEOPLE
        and not bool(window_data.get("enabled", False))
        and window_data.get("start") is None
        and window_data.get("end") is None
    )


def resolve_frontend_route_class(req: HttpRequest, access: AccessContext) -> str:
    raw_url = ""
    if isinstance(req.raw_event, dict):
        raw_url = str(req.raw_event.get("url", "")).strip()
    normalized = normalize_path(raw_url or req.path)
    if "/bff/" in normalized:
        return "bff"
    if access.trusted_ingress:
        return "bff"
    return "api"


def default_frontend_cache_key(*, route_class: str, access_mode: str) -> str:
    return f"frontend_v2/default/{route_class}/{access_mode}"


def default_frontend_cache_keys() -> list[str]:
    keys: list[str] = []
    for route_class in ("api", "bff"):
        for access_mode in ("masked", "full"):
            keys.append(default_frontend_cache_key(route_class=route_class, access_mode=access_mode))
    return keys


def invalidate_default_frontend_responses(snapshot_engine: Any) -> None:
    cache_store = snapshot_engine.get_response_cache_store()
    if cache_store is None:
        return
    for cache_key in default_frontend_cache_keys():
        cache_store.delete(cache_key)


def build_default_frontend_cache_query_hash() -> str:
    payload = {
        "statuses": list(DEFAULT_FRONTEND_CACHE_STATUSES),
        "include_people": DEFAULT_FRONTEND_CACHE_INCLUDE_PEOPLE,
        "limit": DEFAULT_FRONTEND_CACHE_LIMIT,
        "designer": "",
        "window": None,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()[:16]


def response_cache_entry_is_fresh(
    entry: dict[str, Any] | None,
    *,
    source_hash: str,
    route_class: str,
    access_mode: str,
    query_hash: str,
    ttl_minutes: int,
    hour_bucket: str | None,
    now: datetime | None = None,
) -> bool:
    if not isinstance(entry, dict):
        return False
    if str(entry.get("source_hash", "")).strip() != str(source_hash or "").strip():
        return False
    if str(entry.get("route_class", "")).strip() != str(route_class or "").strip():
        return False
    if str(entry.get("access_mode", "")).strip() != str(access_mode or "").strip():
        return False
    if str(entry.get("query_hash", "")).strip() != str(query_hash or "").strip():
        return False
    expected_hour = str(hour_bucket or "").strip()
    if expected_hour != str(entry.get("hour_bucket", "")).strip():
        return False
    cached_at_raw = str(entry.get("cached_at", "")).strip()
    if not cached_at_raw:
        return False
    try:
        cached_at = datetime.fromisoformat(cached_at_raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    current = now or datetime.now(timezone.utc)
    ttl = max(int(ttl_minutes or 0), 1)
    return cached_at >= current - timedelta(minutes=ttl)


def build_response_cache_entry(
    *,
    payload: dict[str, Any],
    source_hash: str,
    route_class: str,
    access_mode: str,
    query_hash: str,
    hour_bucket: str | None,
    cached_at: datetime | None = None,
) -> dict[str, Any]:
    current = cached_at or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return {
        "cached_at": current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_hash": str(source_hash or "").strip(),
        "route_class": str(route_class or "").strip(),
        "access_mode": str(access_mode or "").strip(),
        "query_hash": str(query_hash or "").strip(),
        "hour_bucket": str(hour_bucket or "").strip(),
        "payload": deepcopy(dict(payload or {})),
    }


def cached_payload_with_access(payload: dict[str, Any], access: AccessContext) -> dict[str, Any]:
    cloned = deepcopy(dict(payload or {}))
    meta = dict(cloned.get("meta", {}) or {})
    meta["access"] = {
        "mode": access.mode,
        "trustedIngress": bool(access.trusted_ingress),
        "authenticated": bool(access.authenticated),
        "contour": str(access.contour or "").strip(),
        "userRole": access.user_role,
        "userStatus": access.user_status,
        "fallbackReason": access.fallback_reason,
    }
    cloned["meta"] = meta
    return cloned

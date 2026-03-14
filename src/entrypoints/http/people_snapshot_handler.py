"""Secret-only internal API for the full people snapshot."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from hmac import compare_digest

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response
from src.snapshot_engine import build_snapshot_engine


def _header_map(headers: dict[str, object] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in dict(headers or {}).items():
        lowered = str(key or "").strip().lower()
        if lowered:
            result[lowered] = str(value or "").strip()
    return result


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    target = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return target.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class PeopleSnapshotHandler:
    """Expose the canonical people registry to trusted internal callers only."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def _authorized(self, req: HttpRequest) -> bool:
        api_cfg = dict(getattr(self._ctx.cfg.runtime, "api", {}) or {})
        secret_header = str(
            api_cfg.get("auth_trusted_secret_header", "X-DTM-Proxy-Secret") or "X-DTM-Proxy-Secret"
        ).strip().lower()
        expected_secret = str(self._ctx.deps.get("browser_auth_proxy_secret") or "").strip()
        if not expected_secret:
            return False
        headers = _header_map(req.headers)
        provided = headers.get(secret_header, "")
        return bool(provided) and compare_digest(provided, expected_secret)

    @staticmethod
    def _person_payload(person) -> dict[str, object]:
        return {
            "personId": str(getattr(person, "person_id", "") or "").strip(),
            "name": str(getattr(person, "name", "") or "").strip(),
            "position": str(getattr(person, "position", "") or "").strip(),
            "email": str(getattr(person, "email", "") or "").strip(),
            "emailSecondary": str(getattr(person, "email_secondary", "") or "").strip(),
            "telegram": str(getattr(person, "telegram", "") or "").strip(),
            "telegramId": str(getattr(person, "telegram_id", "") or "").strip(),
            "chatId": str(getattr(person, "chat_id", "") or "").strip(),
            "info": str(getattr(person, "info", "") or "").strip(),
            "vacation": str(getattr(person, "vacation", "") or "").strip(),
            "phone": str(getattr(person, "phone", "") or "").strip(),
            "attributes": {
                str(key): str(value).strip()
                for key, value in sorted(dict(getattr(person, "attributes", {}) or {}).items())
            },
        }

    @staticmethod
    def _payload_hash(payload: list[dict[str, object]]) -> str:
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        method = str(req.method or "GET").strip().upper()
        if method == "ANY":
            method = "GET"
        if method != "GET":
            return None
        if normalize_path(req.path) != "/api/v2/people":
            return None
        if not self._authorized(req):
            return error_response(
                403,
                code="forbidden",
                message="Forbidden.",
                details={"reason": "invalid_secret"},
            )
        try:
            snapshot = build_snapshot_engine(self._ctx).get_people_snapshot()
        except Exception as error:
            return error_response(
                503,
                code="people_snapshot_unavailable",
                message="People snapshot is temporarily unavailable.",
                details={"errorType": type(error).__name__},
            )
        if snapshot is None:
            return error_response(
                503,
                code="people_snapshot_unavailable",
                message="People snapshot is temporarily unavailable.",
                details={"errorType": "people_snapshot_unavailable"},
            )
        people = [self._person_payload(person) for _, person in sorted(snapshot.people_by_name.items())]
        payload_hash = self._payload_hash(people)
        env_name = str(self._ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
        response_payload = {
            "meta": {
                "artifact": "dtm_people_snapshot_v1",
                "contractVersion": "1.0.0",
                "generatedAt": _iso(datetime.now(timezone.utc)),
                "fetchedAt": _iso(getattr(snapshot, "fetched_at_utc", None)),
                "source": {
                    "env": env_name,
                    "sourceId": str(getattr(snapshot, "source_id", "") or "").strip(),
                    "sheetName": str(self._ctx.cfg.tables.sheet_names.get("people", "") or "").strip(),
                    "sheetUrl": None,
                },
                "hash": payload_hash,
            },
            "summary": {"peopleTotal": len(people)},
            "people": people,
        }
        return json_response(200, response_payload)

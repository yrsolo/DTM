from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.commands.model import Command, RequestedBy
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response

from .parser import TelegramUpdateParser


class TelegramWebhookHandler:
    def __init__(self, ctx, parser: TelegramUpdateParser | None = None) -> None:
        self._ctx = ctx
        self._parser = parser or TelegramUpdateParser()

    @staticmethod
    def _header(headers: dict, name: str) -> str:
        target = str(name or "").strip().lower()
        for key, value in dict(headers or {}).items():
            if str(key).strip().lower() == target:
                return str(value or "").strip()
        return ""

    def handle(self, req: HttpRequest):
        if not req.is_http_event:
            return None
        if str(req.method or "").strip().upper() != "POST":
            return None
        path = normalize_path(req.path)
        webhook_path = str(self._ctx.cfg.runtime.telegram.webhook_path or "/telegram").strip() or "/telegram"
        if path not in {webhook_path, "/telegram/webhook"}:
            return None

        secret_required = bool(self._ctx.cfg.runtime.telegram.secret_required)
        expected_secret = str(self._ctx.deps.get("tg_webhook_secret_token", "")).strip()
        actual_secret = self._header(req.headers, "X-Telegram-Bot-Api-Secret-Token")
        if secret_required and (not expected_secret or actual_secret != expected_secret):
            return error_response(403, code="telegram_webhook_forbidden", message="Telegram webhook secret token mismatch.")

        producer = self._ctx.deps.get("command_queue_producer")
        status_store = self._ctx.deps.get("job_status_store")
        if producer is None or status_store is None:
            return error_response(
                503,
                code="queue_unavailable",
                message="Command queue is not configured for current environment.",
            )

        parsed = self._parser.parse(dict(req.body or {}))
        if parsed is None:
            return json_response(200, {"artifact": "telegram_webhook", "status": "ignored", "reason": "unsupported_update"})

        action = self._parser.detect_action(
            parsed,
            bot_username=str(self._ctx.deps.get("tg_bot_username", "")),
            default_chat_id=str(self._ctx.deps.get("default_chat_id", "")),
        )
        if action is None:
            return json_response(200, {"artifact": "telegram_webhook", "status": "ignored", "reason": "unsupported_action"})

        cmd = Command(
            job_id=uuid4().hex,
            type=action.command_type,
            created_at_utc=datetime.now(timezone.utc),
            requested_by=RequestedBy(source="telegram", user_id=parsed.user_id or None, chat_id=parsed.chat_id or None),
            payload=dict(action.payload),
        )
        producer.send(cmd)
        record = status_store.put_queued(cmd)
        return json_response(
            200,
            {
                "artifact": "telegram_webhook",
                "status": "accepted",
                "job_id": cmd.job_id,
                "command_type": cmd.type,
                "queued_at": record.requested_at_utc.isoformat(),
            },
        )

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.commands.model import Command, RequestedBy
from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import error_response, json_response
from src.observability import timed

from .command_router import TelegramCommandRouter
from .parser import TelegramUpdateParser


class TelegramWebhookHandler:
    def __init__(
        self,
        ctx,
        parser: TelegramUpdateParser | None = None,
        command_router: TelegramCommandRouter | None = None,
    ) -> None:
        self._ctx = ctx
        self._parser = parser or TelegramUpdateParser()
        self._command_router = command_router or TelegramCommandRouter()

    @staticmethod
    def _header(headers: dict, name: str) -> str:
        target = str(name or "").strip().lower()
        for key, value in dict(headers or {}).items():
            if str(key).strip().lower() == target:
                return str(value or "").strip()
        return ""

    def handle(self, req: HttpRequest):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        runtime_cfg = getattr(getattr(self._ctx.cfg, "runtime", None), "runtime", None)
        env_name = str(getattr(runtime_cfg, "env_default", "") or "dev")
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
            if metrics is not None:
                metrics.counter(
                    "dtm.telegram.rejected_total",
                    labels={"env": env_name, "module": "telegram", "operation": "webhook", "result": "forbidden"},
                )
            if logger is not None:
                logger.warning("telegram_update_rejected", reason="secret_mismatch")
            return error_response(403, code="telegram_webhook_forbidden", message="Telegram webhook secret token mismatch.")

        producer = self._ctx.deps.get("command_queue_producer")
        status_store = self._ctx.deps.get("job_status_store")
        if producer is None or status_store is None:
            return error_response(
                503,
                code="queue_unavailable",
                message="Command queue is not configured for current environment.",
            )

        with timed(
            metrics,
            "dtm.telegram.enqueue_ms",
            {"env": env_name, "module": "telegram", "operation": "webhook", "result": "accepted"},
        ):
            parsed = self._parser.parse(dict(req.body or {}))
            if parsed is None:
                if metrics is not None:
                    metrics.counter(
                        "dtm.telegram.rejected_total",
                        labels={"env": env_name, "module": "telegram", "operation": "parse", "result": "unsupported_update"},
                    )
                return json_response(200, {"artifact": "telegram_webhook", "status": "ignored", "reason": "unsupported_update"})

            routed = self._command_router.route(
                parsed,
                bot_username=str(self._ctx.deps.get("tg_bot_username", "")),
                default_chat_id=str(self._ctx.deps.get("default_chat_id", "")),
            )
            if routed is None:
                if metrics is not None:
                    metrics.counter(
                        "dtm.telegram.rejected_total",
                        labels={"env": env_name, "module": "telegram", "operation": "route", "result": "unsupported_action"},
                    )
                return json_response(200, {"artifact": "telegram_webhook", "status": "ignored", "reason": "unsupported_action"})

            cmd = Command(
                job_id=uuid4().hex,
                type=routed.command_type,
                created_at_utc=datetime.now(timezone.utc),
                requested_by=RequestedBy(source="telegram", user_id=parsed.user_id or None, chat_id=parsed.chat_id or None),
                payload=dict(routed.payload),
            )
            producer.send(cmd)
            record = status_store.put_queued(cmd)
        if metrics is not None:
            metrics.counter(
                "dtm.telegram.updates_total",
                labels={"env": env_name, "module": "telegram", "operation": "webhook", "result": "accepted"},
            )
            metrics.counter(
                "dtm.telegram.command_total",
                labels={"env": env_name, "module": "telegram", "operation": routed.command_name, "result": "accepted"},
            )
        if logger is not None:
            logger.info(
                "telegram_update_accepted",
                command_name=routed.command_name,
                command_type=routed.command_type,
                chat_type=parsed.chat_type,
            )
        if metrics is not None:
            metrics.counter(
                "dtm.telegram.accepted_total",
                labels={"env": env_name, "module": "telegram", "operation": "webhook", "result": "accepted"},
            )
        return json_response(
            200,
            {
                "artifact": "telegram_webhook",
                "status": "accepted",
                "job_id": cmd.job_id,
                "command_type": cmd.type,
                "command_name": routed.command_name,
                "queued_at": record.requested_at_utc.isoformat(),
            },
        )

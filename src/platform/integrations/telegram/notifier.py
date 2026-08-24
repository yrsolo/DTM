"""Telegram Bot API adapter with scoped proxy/direct failover."""

from __future__ import annotations

import asyncio
from typing import Any

from src.platform.errors import PermanentError, TransientError

from .proxy import MihomoProxySession

_PARSE_ERROR_TOKENS = ("can't parse", "cant parse", "parse entities", "entity")
_TRANSIENT_ERROR_NAMES = {"NetworkError", "RetryAfter", "TimedOut"}
_PERMANENT_ERROR_NAMES = {"BadRequest", "Forbidden", "InvalidToken", "ChatMigrated"}


class TelegramNotifier:
    """Deliver Telegram messages through one explicitly scoped Bot client."""

    def __init__(
        self,
        bot_token: str | None = None,
        default_chat_id: str | int | None = None,
        *,
        proxy_session: MihomoProxySession | None = None,
        metrics: Any = None,
        env_name: str = "unknown",
    ) -> None:
        self._bot_token = str(bot_token or "").strip()
        self._bot: Any = None
        self._proxy_session = proxy_session
        self._proxy_url: str | None = None
        self._metrics = metrics
        self._env_name = str(env_name or "unknown")
        self._active = False
        self.default_chat_id = default_chat_id

    async def __aenter__(self) -> "TelegramNotifier":
        if self._active:
            return self
        if not self._bot_token:
            raise PermanentError("Telegram bot token is empty.", code="telegram_token_missing")
        proxy_url = await self._proxy_session.open() if self._proxy_session is not None else None
        if proxy_url:
            try:
                await self._replace_bot(proxy_url)
                self._proxy_url = proxy_url
                self._active = True
                self._route_metric("proxy")
                return self
            except Exception:
                self._counter("dtm.telegram.delivery_failover_total", result="proxy_preflight")
                await self._proxy_session.close()
        allow_direct = self._proxy_session is None or self._proxy_session.direct_fallback
        if not allow_direct:
            raise TransientError("No healthy Telegram proxy route.", code="telegram_unreachable")
        try:
            await self._replace_bot(None)
        except Exception as error:
            classified = self._classified(error)
            if isinstance(classified, TransientError):
                raise TransientError(
                    "Telegram is unreachable through proxy and direct routes.",
                    code="telegram_unreachable",
                ) from error
            raise classified from error
        self._proxy_url = None
        self._active = True
        self._route_metric("direct")
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:  # noqa: ANN001
        self._active = False
        await self._close_bot()
        if self._proxy_session is not None:
            await self._proxy_session.close()
        self._proxy_url = None

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None = "Markdown",
    ) -> Any:
        if not self._active:
            async with self:
                return await self._send_active(chat_id, text, parse_mode)
        return await self._send_active(chat_id, text, parse_mode)

    async def _send_active(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None,
    ) -> Any:
        try:
            return await self._raw_send(chat_id, text, parse_mode)
        except Exception as error:
            if parse_mode is not None and self._is_parse_error(error):
                return await self._send_without_markup(chat_id, text)
            classified = self._classified(error)
            if not isinstance(classified, TransientError):
                raise classified from error
        if self._proxy_url and self._proxy_session is not None:
            try:
                await self._proxy_session.refresh(exclude_current=True)
            except Exception:
                self._counter("dtm.telegram.delivery_failover_total", result="proxy_refresh_failed")
            else:
                try:
                    await self._replace_bot(self._proxy_url)
                    self._counter("dtm.telegram.delivery_failover_total", result="proxy_refresh")
                    return await self._raw_send(chat_id, text, parse_mode)
                except Exception as error:
                    if parse_mode is not None and self._is_parse_error(error):
                        return await self._send_without_markup(chat_id, text)
                    classified = self._classified(error)
                    if not isinstance(classified, TransientError):
                        raise classified from error
        if self._proxy_session is not None and self._proxy_session.direct_fallback:
            try:
                await self._replace_bot(None)
                self._proxy_url = None
                self._route_metric("direct")
                self._counter("dtm.telegram.delivery_failover_total", result="direct")
                return await self._raw_send(chat_id, text, parse_mode)
            except Exception as error:
                if parse_mode is not None and self._is_parse_error(error):
                    return await self._send_without_markup(chat_id, text)
                classified = self._classified(error)
                if isinstance(classified, TransientError):
                    raise TransientError(
                        "Telegram delivery failed through every configured route.",
                        code="telegram_unreachable",
                    ) from error
                raise classified from error
        raise TransientError(
            "Telegram delivery failed through every configured route.",
            code="telegram_unreachable",
        )

    async def _send_without_markup(self, chat_id: str | int, text: str) -> Any:
        try:
            return await self._raw_send(chat_id, text, None)
        except Exception as error:
            raise self._classified(error) from error

    async def _raw_send(self, chat_id: str | int, text: str, parse_mode: str | None) -> Any:
        if self._bot is None:
            raise TransientError(
                "Telegram sender session is not initialized.",
                code="telegram_sender_not_initialized",
            )
        return await self._bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

    async def _replace_bot(self, proxy_url: str | None) -> None:
        await self._close_bot()
        try:
            from telegram import Bot
            from telegram.request import HTTPXRequest
        except Exception as error:
            raise PermanentError(
                "Telegram adapter dependency is unavailable.",
                code="telegram_dependency_missing",
            ) from error
        request = HTTPXRequest(
            proxy=proxy_url,
            connect_timeout=5.0,
            read_timeout=10.0,
            write_timeout=10.0,
            pool_timeout=5.0,
        )
        bot = Bot(token=self._bot_token, request=request)
        try:
            await bot.initialize()
        except Exception:
            await request.shutdown()
            raise
        self._bot = bot

    async def _close_bot(self) -> None:
        bot = self._bot
        self._bot = None
        if bot is not None:
            try:
                await bot.shutdown()
            except Exception:
                pass

    @staticmethod
    def _is_parse_error(error: Exception) -> bool:
        if type(error).__name__ != "BadRequest":
            return False
        text = str(error).lower()
        return any(token in text for token in _PARSE_ERROR_TOKENS)

    @staticmethod
    def _classified(error: Exception) -> PermanentError | TransientError:
        if isinstance(error, (PermanentError, TransientError)):
            return error
        name = type(error).__name__
        status_code = getattr(error, "status_code", None)
        if name in _TRANSIENT_ERROR_NAMES or getattr(error, "retry_after", None) is not None:
            code = "telegram_rate_limited" if name == "RetryAfter" else "telegram_transient"
            return TransientError(str(error), code=code)
        if status_code in {408, 425, 429, 500, 502, 503, 504}:
            return TransientError(str(error), code=f"telegram_http_{status_code}")
        if name in _PERMANENT_ERROR_NAMES or status_code in {400, 401, 403, 404}:
            return PermanentError(str(error), code="telegram_permanent")
        text = str(error).lower()
        if any(token in text for token in ("timeout", "timed out", "connection", "network")):
            return TransientError(str(error), code="telegram_transient")
        return PermanentError(str(error), code="telegram_unknown")

    def _route_metric(self, route: str) -> None:
        self._counter("dtm.telegram.transport_selected_total", result=route)

    def _counter(self, name: str, *, result: str) -> None:
        if self._metrics is not None:
            self._metrics.counter(
                name,
                labels={
                    "env": self._env_name,
                    "module": "telegram",
                    "operation": "delivery",
                    "result": result,
                },
            )

    def log(self, text: str) -> None:
        if self.default_chat_id is None:
            raise PermanentError(
                "Default Telegram chat id is empty.",
                code="telegram_default_chat_missing",
            )
        asyncio.get_running_loop().create_task(self.alog(text))

    async def alog(self, text: str) -> Any:
        if self.default_chat_id is None:
            raise PermanentError(
                "Default Telegram chat id is empty.",
                code="telegram_default_chat_missing",
            )
        return await self.send_message(self.default_chat_id, text, parse_mode=None)


__all__ = ["TelegramNotifier"]

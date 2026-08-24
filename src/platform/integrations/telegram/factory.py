"""Composition-root factory for scoped Telegram senders."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator

from .notifier import TelegramNotifier
from .proxy import MihomoProxySession, TelegramProxySettings


@dataclass(frozen=True, slots=True)
class TelegramSenderFactory:
    bot_token: str
    default_chat_id: str | int | None
    proxy_settings: TelegramProxySettings
    metrics: Any = None
    logger: Any = None

    @classmethod
    def from_context(cls, ctx) -> "TelegramSenderFactory":  # noqa: ANN001
        telegram = ctx.cfg.runtime.telegram
        deps = ctx.deps
        settings = TelegramProxySettings(
            env_name=str(ctx.cfg.runtime.runtime.env_default),
            delivery_transport=str(telegram.delivery_transport),
            subscription_url=str(deps.get("telegram_proxy_subscription_url", "")).strip(),
            group_name=str(telegram.proxy_group),
            health_url=str(telegram.proxy_health_url),
            startup_timeout_seconds=float(telegram.proxy_startup_timeout_seconds),
            subscription_timeout_seconds=float(telegram.proxy_subscription_timeout_seconds),
            health_timeout_seconds=float(telegram.proxy_health_timeout_seconds),
            cache_ttl_seconds=int(telegram.proxy_cache_ttl_seconds),
            direct_fallback=bool(telegram.direct_fallback),
            binary_path=str(telegram.mihomo_binary_path),
        )
        return cls(
            bot_token=str(deps.get("tg_bot_token", "")).strip(),
            default_chat_id=deps.get("default_chat_id"),
            proxy_settings=settings,
            metrics=deps.get("metrics_client"),
            logger=deps.get("structured_logger"),
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[TelegramNotifier]:
        proxy = MihomoProxySession(
            self.proxy_settings,
            metrics=self.metrics,
            logger=self.logger,
        )
        notifier = TelegramNotifier(
            bot_token=self.bot_token,
            default_chat_id=self.default_chat_id,
            proxy_session=proxy,
            metrics=self.metrics,
            env_name=self.proxy_settings.env_name,
        )
        async with notifier:
            yield notifier


__all__ = ["TelegramSenderFactory"]

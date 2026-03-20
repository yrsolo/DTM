"""Module surface for the telegram interaction context."""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.snapshot.public import get_read_capability
from .internal import TelegramCommandRouter, TelegramSender, TelegramUpdateParser, TelegramWebhookHandler
from .internal.group_query_formatter import GroupQueryFormatter
from .internal.group_query_usecase import GroupQueryUseCase


@dataclass(frozen=True, slots=True)
class TelegramInteractionModule:
    """Own the reserve Telegram interaction contour and its runtime assembly."""

    name: str = "telegram_interaction"

    def update_parser(self):
        return TelegramUpdateParser()

    def command_router(self):
        return TelegramCommandRouter()

    def webhook_handler(self, ctx):
        return TelegramWebhookHandler(
            ctx,
            parser=self.update_parser(),
            command_router=self.command_router(),
        )

    def snapshot_read_capability(self, ctx):
        return get_read_capability(ctx)

    def usecase(self, snapshot_read):
        return GroupQueryUseCase(snapshot_read)

    def group_query_formatter(self):
        return GroupQueryFormatter()

    def sender(self, ctx):
        return TelegramSender(
            bot_token=str(ctx.deps.get("tg_bot_token", "")),
            default_chat_id=ctx.deps.get("default_chat_id"),
        )

    def request(self, **kwargs):
        from .internal.group_query_request import GroupQueryRequest

        return GroupQueryRequest(**kwargs)


def get_module() -> TelegramInteractionModule:
    """Return the canonical module surface for the telegram interaction context."""

    return TelegramInteractionModule()

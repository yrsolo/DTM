"""Local builder for the telegram interaction context."""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.snapshot.public import get_snapshot_engine
from src.notify import GroupQueryFormatter, ReminderUseCase
from src.telegram.command_router import TelegramCommandRouter
from src.telegram.parser import TelegramUpdateParser
from src.telegram.sender import TelegramSender
from src.telegram.webhook import TelegramWebhookHandler


@dataclass(frozen=True, slots=True)
class TelegramInteractionModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "telegram_interaction"

    def build_update_parser(self):
        return TelegramUpdateParser()

    def build_command_router(self):
        return TelegramCommandRouter()

    def build_webhook_handler(self, ctx):
        return TelegramWebhookHandler(
            ctx,
            parser=self.build_update_parser(),
            command_router=self.build_command_router(),
        )

    def build_snapshot_engine(self, ctx):
        return get_snapshot_engine(ctx)

    def build_usecase(self, snapshot_engine):
        return ReminderUseCase(snapshot_engine)

    def build_group_query_formatter(self):
        return GroupQueryFormatter()

    def build_sender(self, ctx):
        return TelegramSender(
            bot_token=str(ctx.deps.get("tg_bot_token", "")),
            default_chat_id=ctx.deps.get("default_chat_id"),
        )


def get_module() -> TelegramInteractionModule:
    """Return the local module instance for the telegram interaction context."""

    return TelegramInteractionModule()

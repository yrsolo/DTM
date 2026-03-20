"""Compatibility wrapper for Telegram webhook intake.

Legacy route import stays in tree, but runtime Telegram handling now lives in
`src.contexts.telegram_interaction.public`.
"""

from __future__ import annotations

from src.contexts.telegram_interaction.public import get_webhook_handler


class GroupQueryHandler:
    def __new__(cls, ctx, *args, **kwargs):  # noqa: ANN002, ANN003
        return get_webhook_handler(ctx)

__all__ = ["GroupQueryHandler"]

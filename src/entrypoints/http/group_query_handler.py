"""Compatibility wrapper for Telegram webhook intake.

Legacy route import stays in tree, but runtime Telegram handling now lives in
`src.telegram.webhook.TelegramWebhookHandler`.
"""

from __future__ import annotations

from src.telegram.webhook import TelegramWebhookHandler as GroupQueryHandler

__all__ = ["GroupQueryHandler"]

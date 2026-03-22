"""Application-owned telegram interaction surface."""

from __future__ import annotations

from src.platform.context import AppContext


class TelegramInteractionApi:
    """Own live webhook and group-query reply assembly."""

    def __init__(self, ctx: AppContext, module) -> None:  # noqa: ANN001
        self._ctx = ctx
        self._module = module

    def webhook_handler(self):
        return self._module.webhook_handler(self._ctx)

    def snapshot_read_api(self):
        return self._module.snapshot_read_api(self._ctx)

    def usecase(self, snapshot_read=None):  # noqa: ANN001
        if snapshot_read is None:
            snapshot_read = self.snapshot_read_api()
        return self._module.usecase(snapshot_read)

    def group_query_formatter(self):
        return self._module.group_query_formatter()

    def sender(self):
        return self._module.sender(self._ctx)

    def request(self, **kwargs):
        return self._module.request(**kwargs)


__all__ = ["TelegramInteractionApi"]

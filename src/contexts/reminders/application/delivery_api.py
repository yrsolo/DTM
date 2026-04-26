"""Application-owned reminder delivery surface."""

from __future__ import annotations

from src.platform.context import AppContext


class ReminderDeliveryApi:
    """Own the live reminder delivery scenario for runtime and queue callers."""

    def __init__(self, ctx: AppContext, module) -> None:  # noqa: ANN001
        self._ctx = ctx
        self._module = module

    def snapshot_read_api(self):
        return self._module.snapshot_read_api(self._ctx)

    def usecase(self, snapshot_read=None):  # noqa: ANN001
        if snapshot_read is None:
            snapshot_read = self.snapshot_read_api()
        return self._module.usecase(snapshot_read)

    def formatter(self):
        return self._module.formatter(self._ctx)

    def sender(self):
        return self._module.sender(self._ctx)

    def enhancer(self, *, mock_external: bool):
        return self._module.enhancer(self._ctx, mock_external=mock_external)

    def llm_model_for_mode(self, mode: str) -> str:
        return self._module.llm_model_for_mode(self._ctx, mode)

    def today_in_runtime_timezone(self):
        return self._module.today_in_runtime_timezone(self._ctx)

    def job_runner(self, **kwargs):
        return self._module.job_runner(**kwargs)

    def request(self, **kwargs):
        return self._module.request(**kwargs)


__all__ = ["ReminderDeliveryApi"]

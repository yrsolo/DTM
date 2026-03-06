from __future__ import annotations

from .model import RenderPlan


class SheetsWriter:
    """Infra adapter that writes RenderPlan to Google Sheets in batches."""

    def apply(self, plan: RenderPlan) -> None:
        raise NotImplementedError

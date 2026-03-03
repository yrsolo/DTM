"""Shared source-policy matrix for API, render, and notify consumers."""

from __future__ import annotations

from dataclasses import dataclass


RENDER_RUNTIME_MODES = frozenset({"timer", "test", "sync-only"})
NOTIFY_RUNTIME_MODES = frozenset({"morning", "test", "reminders-only"})


@dataclass(frozen=True, slots=True)
class SourcePolicyMatrix:
    readmodel_source: str
    notify_source: str
    render_source: str

    def api_reads_ydb(self) -> bool:
        return self.readmodel_source == "ydb"

    def render_reads_ydb(self, mode: str) -> bool:
        return self.render_source == "ydb" and str(mode).strip().lower() in RENDER_RUNTIME_MODES

    def notify_reads_ydb(self, mode: str) -> bool:
        return self.notify_source == "ydb" and str(mode).strip().lower() in NOTIFY_RUNTIME_MODES


def build_source_policy_matrix(
    *,
    readmodel_source: str,
    notify_source: str,
    render_source: str,
) -> SourcePolicyMatrix:
    return SourcePolicyMatrix(
        readmodel_source=str(readmodel_source).strip().lower(),
        notify_source=str(notify_source).strip().lower(),
        render_source=str(render_source).strip().lower(),
    )

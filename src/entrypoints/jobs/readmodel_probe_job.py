"""Readmodel freshness probe helper for main job flow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo


@dataclass(frozen=True)
class ReadmodelProbeRequest:
    mode: str
    render_source: str
    notify_source: str
    ydb_endpoint: str
    ydb_database: str
    ydb_sa_json_credentials: str | None
    ydb_sa_key_file: str | None
    marker_builder: Callable[[object | None], dict[str, object]]
    safe_print: Callable[[str], None]
    repo_cls: type[FrontendReadmodelRepo] = FrontendReadmodelRepo


def run_readmodel_freshness_probe(
    request: ReadmodelProbeRequest,
) -> None:
    if not (
        request.mode in {"timer", "test", "morning", "reminders-only", "sync-only"}
        and (request.render_source == "ydb" or request.notify_source == "ydb")
    ):
        return
    try:
        readmodel_repo = request.repo_cls(
            endpoint=request.ydb_endpoint,
            database=request.ydb_database,
            sa_json_credentials=request.ydb_sa_json_credentials,
            sa_key_file=request.ydb_sa_key_file,
            ensure_schema=False,
        )
        marker = request.marker_builder(readmodel_repo.get_readmodel("frontend_v2:default"))
        marker["render_source"] = request.render_source
        marker["notify_source"] = request.notify_source
        request.safe_print("readmodel_freshness=" + json.dumps(marker, ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        request.safe_print(f"readmodel_freshness_error={str(exc)}")

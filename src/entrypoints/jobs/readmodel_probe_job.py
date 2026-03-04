"""Readmodel freshness probe helper for main job flow."""

from __future__ import annotations

import json
from typing import Any, Callable

from src.adapters.ydb.readmodel_repo import FrontendReadmodelRepo


def run_readmodel_freshness_probe(
    *,
    mode: str,
    render_source: str,
    notify_source: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str | None,
    ydb_sa_key_file: str | None,
    marker_builder: Callable[[object | None], dict[str, object]],
    safe_print: Callable[[str], None],
    repo_cls: type[FrontendReadmodelRepo] = FrontendReadmodelRepo,
) -> None:
    if not (
        mode in {"timer", "test", "morning", "reminders-only", "sync-only"}
        and (render_source == "ydb" or notify_source == "ydb")
    ):
        return
    try:
        readmodel_repo = repo_cls(
            endpoint=ydb_endpoint,
            database=ydb_database,
            sa_json_credentials=ydb_sa_json_credentials,
            sa_key_file=ydb_sa_key_file,
            ensure_schema=False,
        )
        marker = marker_builder(readmodel_repo.get_readmodel("frontend_v2:default"))
        marker["render_source"] = render_source
        marker["notify_source"] = notify_source
        safe_print("readmodel_freshness=" + json.dumps(marker, ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        safe_print(f"readmodel_freshness_error={str(exc)}")

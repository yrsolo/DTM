"""Snapshot engine facade and builders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.app.context import AppContext
from src.snapshot_engine.prep_builder import PrepBuilder
from src.snapshot_engine.query_engine import FrontendV2Query, SnapshotQueryEngine
from src.snapshot_engine.update_job import (
    SheetSnapshotHasher,
    SheetsTaskNormalizer,
    TaskSourceSheetsAdapter,
    UpdateJob,
)


@dataclass(frozen=True)
class SnapshotFrontendQuery:
    statuses: list[str]
    designer: str
    limit: int
    include_people: bool
    window_enabled: bool
    window_start: date | None
    window_end: date | None
    window_mode: str = "intersects"


class SnapshotEngine:
    def __init__(
        self,
        *,
        raw_cache: Any,
        prep_cache: Any,
        query_engine: SnapshotQueryEngine,
        update_job_factory: Any,
    ) -> None:
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._query_engine = query_engine
        self._update_job_factory = update_job_factory

    def update(self, *, task_source: Any, force: bool = False) -> Any:
        update_job = self._update_job_factory(task_source)
        return update_job.run(force=force)

    def frontend_v2(self, query: SnapshotFrontendQuery) -> dict[str, Any]:
        prep = self._prep_cache.get()
        if prep is None:
            raise RuntimeError("prep_snapshot_unavailable")
        return self._query_engine.query_frontend_v2(
            prep,
            FrontendV2Query(
                statuses=list(query.statuses),
                designer=query.designer,
                limit=query.limit,
                include_people=query.include_people,
                window_enabled=query.window_enabled,
                window_start=query.window_start,
                window_end=query.window_end,
                window_mode=query.window_mode,
            ),
        )

    def get_prep_snapshot(self) -> Any:
        return self._prep_cache.get()


def _resolve_env_prefix(value: str, env_name: str) -> str:
    token = "{env}"
    cleaned = str(value or "").strip()
    if token in cleaned:
        return cleaned.replace(token, str(env_name or "").strip().lower() or "dev")
    return cleaned


def build_snapshot_engine(ctx: AppContext) -> SnapshotEngine:
    from src.snapshot_engine.stores.s3_store import build_s3_stores

    cfg = ctx.cfg
    deps = ctx.deps
    snap_cfg = cfg.runtime.snapshot_engine
    db_cfg = cfg.db.object_storage
    endpoint_url = str(db_cfg.get("endpoint_url_default", "")).strip()
    env_name = str(cfg.runtime.runtime.env_default).strip().lower() or "dev"
    raw_cache, prep_cache, extra_store = build_s3_stores(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        raw_key=_resolve_env_prefix(str(snap_cfg.prefix_raw), env_name),
        prep_key=_resolve_env_prefix(str(snap_cfg.prefix_prep), env_name),
        extra_prefix=_resolve_env_prefix(str(snap_cfg.prefix_extra), env_name),
    )
    prep_builder = PrepBuilder(extra_store)
    query_engine = SnapshotQueryEngine(
        env_name=cfg.runtime.runtime.env_default,
        source_sheet_name=str(cfg.tables.google_sheets.get("source_sheet_name_default", "")),
    )

    def _update_job_factory(task_source: Any) -> UpdateJob:
        return UpdateJob(
            source=TaskSourceSheetsAdapter(task_source),
            hasher=SheetSnapshotHasher(),
            normalizer=SheetsTaskNormalizer(),
            raw_cache=raw_cache,
            prep_cache=prep_cache,
            prep_builder=prep_builder,
        )

    return SnapshotEngine(
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        query_engine=query_engine,
        update_job_factory=_update_job_factory,
    )

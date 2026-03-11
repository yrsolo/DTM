"""Snapshot engine facade and builders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.app.context import AppContext
from src.services.errors import UserError

from src.snapshot_engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.snapshot_engine.prep_builder import PrepBuilder
from src.snapshot_engine.query_engine import FrontendV2Query, SnapshotQueryEngine
from src.snapshot_engine.update_job import (
    PeopleSnapshotUpdater,
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
        extra_store: Any,
        people_store: Any,
        query_engine: SnapshotQueryEngine,
        prep_builder: PrepBuilder,
        update_job_factory: Any,
        people_update_job_factory: Any,
    ) -> None:
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._extra_store = extra_store
        self._people_store = people_store
        self._query_engine = query_engine
        self._prep_builder = prep_builder
        self._update_job_factory = update_job_factory
        self._people_update_job_factory = people_update_job_factory

    def update(self, *, task_source: Any, force: bool = False) -> Any:
        update_job = self._update_job_factory(task_source)
        result = update_job.run(force=force)
        people_updater = self._people_update_job_factory(task_source)
        people_updater.run(TaskSourceSheetsAdapter(task_source))
        return result

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

    def get_raw_snapshot(self) -> Any:
        return self._raw_cache.get()

    def get_people_snapshot(self) -> Any:
        return self._people_store.get()

    def attach_file_metadata(self, *, task_id: str, attachment: AttachmentMeta) -> dict[str, Any]:
        raw = self._raw_cache.get()
        if raw is None:
            raise UserError("Raw snapshot is unavailable.", code="raw_snapshot_unavailable")
        task_key = str(task_id or "").strip()
        if not task_key or task_key not in raw.tasks_by_id:
            raise UserError("Task was not found in current snapshot.", code="task_not_found")
        extra_snapshot = self._extra_store.get_snapshot()
        items_by_task_id = dict(extra_snapshot.items_by_task_id)
        current = items_by_task_id.get(task_key) or TaskExtra(task_id=task_key)
        attachments = [item for item in list(current.attachments or []) if str(item.id) != str(attachment.id)]
        attachments.append(attachment)
        attachments.sort(key=lambda item: (item.uploaded_at_utc.isoformat(), item.id))
        updated = TaskExtra(
            task_id=current.task_id,
            orphaned=bool(current.orphaned),
            updated_at_utc=attachment.uploaded_at_utc,
            attachments=attachments,
            docs=list(current.docs),
            links=list(current.links),
            notes=str(current.notes),
            artifacts=list(current.artifacts),
        )
        items_by_task_id[task_key] = updated
        self._extra_store.put_snapshot(
            ExtraSnapshot(
                version=max(int(extra_snapshot.version or 2), 1),
                updated_at_utc=datetime.now(timezone.utc),
                items_by_task_id=items_by_task_id,
            )
        )
        prep_result = self._prep_builder.build(raw)
        self._prep_cache.put(prep_result.prep)
        return {
            "artifact": "attach_task_file",
            "status": "ok",
            "task_id": task_key,
            "attachment_id": str(attachment.id),
            "attachments_total": len(attachments),
            "prep_written": True,
        }


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
    raw_cache, prep_cache, extra_store, people_store = build_s3_stores(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        raw_key=_resolve_env_prefix(str(snap_cfg.prefix_raw), env_name),
        prep_key=_resolve_env_prefix(str(snap_cfg.prefix_prep), env_name),
        extra_prefix=_resolve_env_prefix(str(snap_cfg.prefix_extra), env_name),
        people_key=_resolve_env_prefix(str(snap_cfg.prefix_people), env_name),
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

    def _people_update_job_factory(_task_source: Any) -> PeopleSnapshotUpdater:
        people_field_map = dict(cfg.tables.field_maps.get("people", {}))
        return PeopleSnapshotUpdater(
            people_store=people_store,
            source_id=f"sheet:{cfg.tables.google_sheets.get('source_sheet_name_default', '')}:people:A1:Z200",
            people_field_map=people_field_map,
        )

    return SnapshotEngine(
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        extra_store=extra_store,
        people_store=people_store,
        query_engine=query_engine,
        prep_builder=prep_builder,
        update_job_factory=_update_job_factory,
        people_update_job_factory=_people_update_job_factory,
    )

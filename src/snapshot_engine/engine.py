"""Snapshot engine facade and builders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.app.context import AppContext
from src.contexts.attachments.contracts import (
    ATTACHMENT_STATUS_DELETED,
    ATTACHMENT_STATUS_PENDING_UPLOAD,
    ATTACHMENT_STATUS_READY,
    ATTACHMENT_STATUS_UPLOADED_UNVERIFIED,
    AttachmentMetadataStore,
)
from src.services.errors import AppError, UserError

from src.snapshot_engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.snapshot_engine.prep_builder import PrepBuilder
from src.snapshot_engine.query_engine import FrontendV2Query, SnapshotQueryEngine
from src.snapshot_engine.update_job import (
    PeopleSnapshotUpdater,
    SheetSnapshotHasher,
    SheetsTaskNormalizer,
    TaskSourceSheetsAdapter,
    UpdateJob,
    normalize_person_yandex_email,
    normalize_person_lookup_value,
    normalize_person_name,
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
        attachment_bucket: str,
        raw_cache: Any,
        prep_cache: Any,
        extra_store: Any,
        people_store: Any,
        response_cache_store: Any,
        query_engine: SnapshotQueryEngine,
        prep_builder: PrepBuilder,
        update_job_factory: Any,
        people_update_job_factory: Any,
    ) -> None:
        self._attachment_bucket = str(attachment_bucket or "").strip()
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._extra_store = extra_store
        self._people_store = people_store
        self._response_cache_store = response_cache_store
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

    def find_by_telegram_id(self, telegram_id: str) -> Any | None:
        lookup = normalize_person_lookup_value(telegram_id)
        if not lookup:
            return None
        snapshot = self.get_people_snapshot()
        if snapshot is None:
            return None
        for person in snapshot.people_by_name.values():
            if normalize_person_lookup_value(getattr(person, "telegram_id", "")) == lookup:
                return person
        return None

    def find_by_chat_id(self, chat_id: str) -> Any | None:
        lookup = normalize_person_lookup_value(chat_id)
        if not lookup:
            return None
        snapshot = self.get_people_snapshot()
        if snapshot is None:
            return None
        for person in snapshot.people_by_name.values():
            if normalize_person_lookup_value(getattr(person, "chat_id", "")) == lookup:
                return person
        return None

    def find_by_yandex_email(self, email: str) -> Any | None:
        lookup = normalize_person_yandex_email(email)
        if not lookup:
            return None
        snapshot = self.get_people_snapshot()
        if snapshot is None:
            return None
        for person in snapshot.people_by_name.values():
            primary = normalize_person_yandex_email(getattr(person, "yandex_email", ""))
            if lookup == primary:
                return person
        return None

    def find_by_email(self, email: str) -> Any | None:
        return self.find_by_yandex_email(email)

    def find_by_name(self, name: str) -> Any | None:
        lookup = normalize_person_name(name)
        if not lookup:
            return None
        snapshot = self.get_people_snapshot()
        if snapshot is None:
            return None
        return snapshot.people_by_name.get(lookup)

    def get_response_cache_store(self) -> Any:
        return self._response_cache_store

    def attach_file_metadata(self, *, task_id: str, attachment: AttachmentMeta) -> dict[str, Any]:
        raw = self._raw_cache.get()
        if raw is None:
            raise UserError("Raw snapshot is unavailable.", code="raw_snapshot_unavailable")
        task_key = str(task_id or "").strip()
        if not task_key or task_key not in raw.tasks_by_id:
            raise UserError("Task was not found in current snapshot.", code="task_not_found")
        metadata_store = self.get_attachment_metadata_store()
        existing = metadata_store.list_by_task_id(task_key)
        payload = attachment.to_dict()
        payload["task_id"] = task_key
        payload["status"] = ATTACHMENT_STATUS_READY
        payload["snapshot_visible"] = True
        ready_attachment = AttachmentMeta.from_dict(payload)
        extra_snapshot = self._extra_store.get_snapshot()
        items_by_task_id = dict(extra_snapshot.items_by_task_id)
        current = items_by_task_id.get(task_key) or TaskExtra(task_id=task_key)
        attachments = [item for item in list(existing or []) if str(item.attachment_id) != str(ready_attachment.attachment_id)]
        attachments.append(ready_attachment)
        attachments.sort(key=lambda item: (str(item.sort_key), item.uploaded_at_utc.isoformat(), item.attachment_id))
        items_by_task_id[task_key] = TaskExtra(
            task_id=current.task_id,
            orphaned=bool(current.orphaned),
            updated_at_utc=datetime.now(timezone.utc),
            attachments=attachments,
            docs=list(current.docs),
            links=list(current.links),
            notes=str(current.notes),
            artifacts=list(current.artifacts),
        )
        self._extra_store.put_snapshot(ExtraSnapshot(version=max(int(extra_snapshot.version or 2), 1), updated_at_utc=datetime.now(timezone.utc), items_by_task_id=items_by_task_id))
        prep_result = self._prep_builder.build(raw)
        self._prep_cache.put(prep_result.prep)
        return {
            "artifact": "attach_task_file",
            "status": "ok",
            "task_id": task_key,
            "attachment_id": str(ready_attachment.attachment_id),
            "attachments_total": len(attachments),
            "prep_written": True,
        }

    def delete_attachment(self, *, task_id: str, attachment_id: str) -> dict[str, Any]:
        raw = self._raw_cache.get()
        if raw is None:
            raise UserError("Raw snapshot is unavailable.", code="raw_snapshot_unavailable")
        task_key = str(task_id or "").strip()
        if not task_key or task_key not in raw.tasks_by_id:
            raise UserError("Task was not found in current snapshot.", code="task_not_found")
        extra_snapshot = self._extra_store.get_snapshot()
        current = dict(extra_snapshot.items_by_task_id or {}).get(task_key)
        if current is None:
            raise UserError("Attachment was not found.", code="attachment_not_found")
        attachments = [item for item in list(current.attachments or []) if str(item.attachment_id) != str(attachment_id or "").strip()]
        if len(attachments) == len(list(current.attachments or [])):
            raise UserError("Attachment was not found.", code="attachment_not_found")
        items_by_task_id = dict(extra_snapshot.items_by_task_id)
        items_by_task_id[task_key] = TaskExtra(
            task_id=current.task_id,
            orphaned=bool(current.orphaned),
            updated_at_utc=datetime.now(timezone.utc),
            attachments=attachments,
            docs=list(current.docs),
            links=list(current.links),
            notes=str(current.notes),
            artifacts=list(current.artifacts),
        )
        self._extra_store.put_snapshot(ExtraSnapshot(version=max(int(extra_snapshot.version or 2), 1), updated_at_utc=datetime.now(timezone.utc), items_by_task_id=items_by_task_id))
        prep_result = self._prep_builder.build(raw)
        self._prep_cache.put(prep_result.prep)
        return {
            "artifact": "delete_task_attachment",
            "status": "ok",
            "task_id": task_key,
            "attachment_id": str(attachment_id or "").strip(),
            "attachments_total": len(attachments),
            "prep_written": True,
        }

    def cleanup_stale_attachments(
        self,
        *,
        ttl_seconds: int,
        delete_object: Any,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        now = now_utc or datetime.now(timezone.utc)
        ttl = max(int(ttl_seconds or 0), 1)
        stale_before = now.timestamp() - ttl
        extra_snapshot = self._extra_store.get_snapshot()
        items_by_task_id = dict(extra_snapshot.items_by_task_id or {})
        changed = False
        tasks_touched = 0
        warnings: list[str] = []
        counts = {
            ATTACHMENT_STATUS_PENDING_UPLOAD: 0,
            ATTACHMENT_STATUS_UPLOADED_UNVERIFIED: 0,
            ATTACHMENT_STATUS_DELETED: 0,
        }
        for task_id, current in list(items_by_task_id.items()):
            task_key = str(task_id or "").strip()
            if not task_key:
                continue
            current_attachments = list(current.attachments or [])
            kept_attachments: list[AttachmentMeta] = []
            task_changed = False
            for item in current_attachments:
                attachment_id = str(getattr(item, "attachment_id", "") or "").strip()
                item_task_id = str(getattr(item, "task_id", "") or "").strip()
                if not attachment_id or not item_task_id or item_task_id != task_key:
                    kept_attachments.append(item)
                    continue
                status = str(getattr(item, "status", "") or "").strip().lower()
                if status not in counts:
                    kept_attachments.append(item)
                    continue
                reference_time = self._cleanup_reference_time(item)
                if reference_time is None or reference_time.timestamp() >= stale_before:
                    kept_attachments.append(item)
                    continue
                storage_key = str(getattr(item, "storage_key", "") or getattr(item, "key", "") or "").strip()
                if storage_key:
                    try:
                        delete_object(key=storage_key)
                    except AppError as error:
                        warnings.append(f"{task_key}:{attachment_id}:{error.code}")
                        kept_attachments.append(item)
                        continue
                counts[status] += 1
                task_changed = True
                changed = True
            if not task_changed:
                continue
            tasks_touched += 1
            items_by_task_id[task_key] = TaskExtra(
                task_id=current.task_id,
                orphaned=bool(current.orphaned),
                updated_at_utc=now,
                attachments=kept_attachments,
                docs=list(current.docs),
                links=list(current.links),
                notes=str(current.notes),
                artifacts=list(current.artifacts),
            )
        prep_written = False
        if changed:
            self._extra_store.put_snapshot(
                ExtraSnapshot(
                    version=max(int(extra_snapshot.version or 2), 1),
                    updated_at_utc=now,
                    items_by_task_id=items_by_task_id,
                )
            )
            raw = self._raw_cache.get()
            if raw is not None:
                prep_result = self._prep_builder.build(raw)
                self._prep_cache.put(prep_result.prep)
                prep_written = True
        return {
            "artifact": "cleanup_task_attachments",
            "status": "ok",
            "ttl_seconds": ttl,
            "pending_removed": counts[ATTACHMENT_STATUS_PENDING_UPLOAD],
            "uploaded_unverified_removed": counts[ATTACHMENT_STATUS_UPLOADED_UNVERIFIED],
            "deleted_removed": counts[ATTACHMENT_STATUS_DELETED],
            "tasks_touched": tasks_touched,
            "prep_written": prep_written,
            "warnings": warnings,
        }

    @staticmethod
    def _cleanup_reference_time(item: AttachmentMeta) -> datetime | None:
        status = str(getattr(item, "status", "") or "").strip().lower()
        if status == ATTACHMENT_STATUS_PENDING_UPLOAD:
            return getattr(item, "uploaded_at_utc", None)
        if status == ATTACHMENT_STATUS_UPLOADED_UNVERIFIED:
            return getattr(item, "verified_at_utc", None) or getattr(item, "uploaded_at_utc", None)
        if status == ATTACHMENT_STATUS_DELETED:
            return getattr(item, "deleted_at_utc", None)
        return None

    def get_attachment_metadata_store(self) -> AttachmentMetadataStore:
        return AttachmentMetadataStore(self._extra_store, bucket=self._attachment_bucket)


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
    raw_cache, prep_cache, extra_store, people_store, response_cache_store = build_s3_stores(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        raw_key=_resolve_env_prefix(str(snap_cfg.prefix_raw), env_name),
        prep_key=_resolve_env_prefix(str(snap_cfg.prefix_prep), env_name),
        extra_prefix=_resolve_env_prefix(str(snap_cfg.prefix_extra), env_name),
        people_key=_resolve_env_prefix(str(snap_cfg.prefix_people), env_name),
        response_prefix=_resolve_env_prefix(str(snap_cfg.prefix_responses), env_name),
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
        attachment_bucket=str(snap_cfg.bucket).strip(),
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        extra_store=extra_store,
        people_store=people_store,
        response_cache_store=response_cache_store,
        query_engine=query_engine,
        prep_builder=prep_builder,
        update_job_factory=_update_job_factory,
        people_update_job_factory=_people_update_job_factory,
    )

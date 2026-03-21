"""Snapshot engine facade and builders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.platform.context import AppContext
from src.contexts.attachments.contracts import (
    ATTACHMENT_STATUS_DELETED,
    ATTACHMENT_STATUS_PENDING_UPLOAD,
    ATTACHMENT_STATUS_READY,
    ATTACHMENT_STATUS_UPLOADED_UNVERIFIED,
    AttachmentMetadataStore,
)
from src.platform.errors import AppError, UserError

from src.contexts.snapshot.internal.attachment_mutations import SnapshotAttachmentMutationService
from src.contexts.snapshot.internal.engine.model import AttachmentMeta, ExtraSnapshot, TaskExtra
from src.contexts.snapshot.internal.engine.prep_builder import PrepBuilder
from src.contexts.snapshot.internal.engine.query_engine import FrontendV2Query, SnapshotQueryEngine
from src.contexts.snapshot.internal.engine.update_job import (
    TaskSourceSheetsAdapter,
    normalize_person_yandex_email,
    normalize_person_lookup_value,
    normalize_person_name,
)
from src.contexts.snapshot.internal.runtime_binding import SnapshotRuntimeBinding, build_snapshot_runtime_binding


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
        self._attachment_mutations = SnapshotAttachmentMutationService(
            attachment_bucket=self._attachment_bucket,
            raw_cache=self._raw_cache,
            prep_cache=self._prep_cache,
            extra_store=self._extra_store,
            prep_builder=self._prep_builder,
        )

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
        return self._attachment_mutations.attach_file_metadata(task_id=task_id, attachment=attachment)

    def delete_attachment(self, *, task_id: str, attachment_id: str) -> dict[str, Any]:
        return self._attachment_mutations.delete_attachment(task_id=task_id, attachment_id=attachment_id)

    def cleanup_stale_attachments(
        self,
        *,
        ttl_seconds: int,
        delete_object: Any,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        return self._attachment_mutations.cleanup_stale_attachments(
            ttl_seconds=ttl_seconds,
            delete_object=delete_object,
            now_utc=now_utc,
        )

    def get_attachment_metadata_store(self) -> AttachmentMetadataStore:
        return self._attachment_mutations.get_attachment_metadata_store()


def build_snapshot_engine_from_runtime(binding: SnapshotRuntimeBinding) -> SnapshotEngine:
    return SnapshotEngine(
        attachment_bucket=binding.attachment_bucket,
        raw_cache=binding.raw_cache,
        prep_cache=binding.prep_cache,
        extra_store=binding.extra_store,
        people_store=binding.people_store,
        response_cache_store=binding.response_cache_store,
        query_engine=binding.query_engine,
        prep_builder=binding.prep_builder,
        update_job_factory=binding.update_job_factory,
        people_update_job_factory=binding.people_update_job_factory,
    )


def build_snapshot_engine(ctx: AppContext) -> SnapshotEngine:
    return build_snapshot_engine_from_runtime(build_snapshot_runtime_binding(ctx))

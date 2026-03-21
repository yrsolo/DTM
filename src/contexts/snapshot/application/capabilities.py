"""Contract-first application APIs for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.attachments.contracts import AttachmentMetadataStore
from src.contexts.snapshot.internal.engine.engine import FrontendV2Query, build_snapshot_engine_from_runtime
from src.contexts.snapshot.internal.engine.update_job import TaskSourceSheetsAdapter
from src.contexts.snapshot.internal.runtime_binding import SnapshotRuntimeBinding


@dataclass(slots=True)
class SnapshotReadApi:
    """Narrow read API exposed to external contexts."""

    _runtime: SnapshotRuntimeBinding

    def get_prep_snapshot(self):
        return self._runtime.prep_cache.get()

    def get_people_snapshot(self):
        return self._runtime.people_store.get()


@dataclass(slots=True)
class SnapshotQueryApi:
    """Read/query API for HTTP and access-facing consumers."""

    _runtime: SnapshotRuntimeBinding

    def get_prep_snapshot(self):
        return self._runtime.prep_cache.get()

    def get_raw_snapshot(self):
        return self._runtime.raw_cache.get()

    def get_people_snapshot(self):
        return self._runtime.people_store.get()

    def get_response_cache_store(self):
        return self._runtime.response_cache_store

    def frontend_v2(self, query):
        prep = self.get_prep_snapshot()
        if prep is None:
            raise RuntimeError("prep_snapshot_unavailable")
        return self._runtime.query_engine.query_frontend_v2(
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


@dataclass(slots=True)
class SnapshotAttachmentApi:
    """Attachment-specific API exposed to external contexts."""

    _runtime: SnapshotRuntimeBinding
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = build_snapshot_engine_from_runtime(self._runtime)
        return self._engine

    def get_attachment_metadata_store(self):
        return AttachmentMetadataStore(
            self._runtime.extra_store,
            bucket=self._runtime.attachment_bucket,
        )

    def get_prep_snapshot(self):
        return self._runtime.prep_cache.get()

    def attach_file_metadata(self, *, task_id: str, attachment):
        return self._bound_engine().attach_file_metadata(task_id=task_id, attachment=attachment)

    def delete_attachment(self, *, task_id: str, attachment_id: str):
        return self._bound_engine().delete_attachment(task_id=task_id, attachment_id=attachment_id)

    def cleanup_stale_attachments(self, *, ttl_seconds: int, delete_object):
        return self._bound_engine().cleanup_stale_attachments(
            ttl_seconds=ttl_seconds,
            delete_object=delete_object,
        )

    def get_response_cache_store(self):
        return self._runtime.response_cache_store


@dataclass(slots=True)
class SnapshotUpdateApi:
    """Snapshot update API exposed to runtime orchestration."""

    _runtime: SnapshotRuntimeBinding

    def update(self, *, task_source: Any, force: bool = False):
        update_job = self._runtime.update_job_factory(task_source)
        result = update_job.run(force=force)
        people_updater = self._runtime.people_update_job_factory(task_source)
        people_updater.run(TaskSourceSheetsAdapter(task_source))
        return result


__all__ = [
    "SnapshotAttachmentApi",
    "SnapshotQueryApi",
    "SnapshotReadApi",
    "SnapshotUpdateApi",
]

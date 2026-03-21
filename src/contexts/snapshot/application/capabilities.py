"""Contract-first application APIs for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.snapshot.internal.engine import build_snapshot_engine


@dataclass(slots=True)
class SnapshotReadApi:
    """Narrow read API exposed to external contexts."""

    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = build_snapshot_engine(self._ctx)
        return self._engine

    def get_prep_snapshot(self):
        return self._bound_engine().get_prep_snapshot()

    def get_people_snapshot(self):
        return self._bound_engine().get_people_snapshot()


@dataclass(slots=True)
class SnapshotQueryApi:
    """Read/query API for HTTP and access-facing consumers."""

    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = build_snapshot_engine(self._ctx)
        return self._engine

    def get_prep_snapshot(self):
        return self._bound_engine().get_prep_snapshot()

    def get_raw_snapshot(self):
        return self._bound_engine().get_raw_snapshot()

    def get_people_snapshot(self):
        return self._bound_engine().get_people_snapshot()

    def get_response_cache_store(self):
        return self._bound_engine().get_response_cache_store()

    def frontend_v2(self, query):
        return self._bound_engine().frontend_v2(query)


@dataclass(slots=True)
class SnapshotAttachmentApi:
    """Attachment-specific API exposed to external contexts."""

    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = build_snapshot_engine(self._ctx)
        return self._engine

    def get_attachment_metadata_store(self):
        return self._bound_engine().get_attachment_metadata_store()

    def get_prep_snapshot(self):
        return self._bound_engine().get_prep_snapshot()

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
        return self._bound_engine().get_response_cache_store()


@dataclass(slots=True)
class SnapshotUpdateApi:
    """Snapshot update API exposed to runtime orchestration."""

    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = build_snapshot_engine(self._ctx)
        return self._engine

    def update(self, *, task_source: Any, force: bool = False):
        return self._bound_engine().update(task_source=task_source, force=force)


__all__ = [
    "SnapshotAttachmentApi",
    "SnapshotQueryApi",
    "SnapshotReadApi",
    "SnapshotUpdateApi",
]

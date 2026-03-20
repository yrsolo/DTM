"""Local builder for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.snapshot.internal.engine import build_snapshot_engine


@dataclass(slots=True)
class SnapshotReadCapability:
    """Narrow read capability exposed to external contexts."""

    _module: "SnapshotModule"
    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = self._module.build_engine(self._ctx)
        return self._engine

    def get_prep_snapshot(self):
        return self._bound_engine().get_prep_snapshot()

    def get_people_snapshot(self):
        return self._bound_engine().get_people_snapshot()


@dataclass(slots=True)
class SnapshotQueryCapability:
    """Read/query capability for HTTP and access-facing consumers."""

    _module: "SnapshotModule"
    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = self._module.build_engine(self._ctx)
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
class SnapshotAttachmentCapability:
    """Attachment-specific mutation capability exposed to external contexts."""

    _module: "SnapshotModule"
    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = self._module.build_engine(self._ctx)
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
class SnapshotUpdateCapability:
    """Snapshot update capability exposed to runtime orchestration."""

    _module: "SnapshotModule"
    _ctx: Any
    _engine: Any | None = None

    def _bound_engine(self):
        if self._engine is None:
            self._engine = self._module.build_engine(self._ctx)
        return self._engine

    def update(self, *, task_source: Any, force: bool = False):
        return self._bound_engine().update(task_source=task_source, force=force)


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "snapshot"

    def build_engine(self, ctx):
        return build_snapshot_engine(ctx)

    def build_read_capability(self, ctx) -> SnapshotReadCapability:
        return SnapshotReadCapability(self, ctx)

    def build_attachment_capability(self, ctx) -> SnapshotAttachmentCapability:
        return SnapshotAttachmentCapability(self, ctx)

    def build_query_capability(self, ctx) -> SnapshotQueryCapability:
        return SnapshotQueryCapability(self, ctx)

    def build_update_capability(self, ctx) -> SnapshotUpdateCapability:
        return SnapshotUpdateCapability(self, ctx)

    def get_prep_snapshot(self, ctx):
        return self.build_engine(ctx).get_prep_snapshot()

    def get_raw_snapshot(self, ctx):
        return self.build_engine(ctx).get_raw_snapshot()

    def get_people_snapshot(self, ctx):
        return self.build_engine(ctx).get_people_snapshot()

    def get_response_cache_store(self, ctx):
        return self.build_engine(ctx).get_response_cache_store()

    def query_frontend_v2(self, ctx, query):
        return self.build_engine(ctx).frontend_v2(query)


def get_module() -> SnapshotModule:
    """Return the local module instance for the snapshot context."""

    return SnapshotModule()

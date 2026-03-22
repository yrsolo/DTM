"""Contract-first application APIs for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.contexts.snapshot.internal.attachment_mutations import SnapshotAttachmentMutationService
from src.contexts.snapshot.internal.engine.engine import FrontendV2Query


@dataclass(slots=True)
class SnapshotReadApi:
    """Narrow read API exposed to external contexts."""

    _prep_snapshot_getter: Callable[[], Any]
    _people_snapshot_getter: Callable[[], Any]

    def get_prep_snapshot(self):
        return self._prep_snapshot_getter()

    def get_people_snapshot(self):
        return self._people_snapshot_getter()


@dataclass(slots=True)
class SnapshotQueryApi:
    """Read/query API for HTTP and access-facing consumers."""

    _prep_snapshot_getter: Callable[[], Any]
    _raw_snapshot_getter: Callable[[], Any]
    _people_snapshot_getter: Callable[[], Any]
    _response_cache_store: Any
    _frontend_query_executor: Callable[[Any, FrontendV2Query], dict[str, Any]]

    def get_prep_snapshot(self):
        return self._prep_snapshot_getter()

    def get_raw_snapshot(self):
        return self._raw_snapshot_getter()

    def get_people_snapshot(self):
        return self._people_snapshot_getter()

    def get_response_cache_store(self):
        return self._response_cache_store

    def frontend_v2(self, query):
        prep = self.get_prep_snapshot()
        if prep is None:
            raise RuntimeError("prep_snapshot_unavailable")
        return self._frontend_query_executor(
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
            )
        )


@dataclass(slots=True)
class SnapshotAttachmentApi:
    """Attachment-specific API exposed to external contexts."""

    _prep_snapshot_getter: Callable[[], Any]
    _response_cache_store: Any
    _mutation_service_builder: Callable[[], SnapshotAttachmentMutationService]
    _mutations: SnapshotAttachmentMutationService | None = None

    def _mutation_service(self) -> SnapshotAttachmentMutationService:
        if self._mutations is None:
            self._mutations = self._mutation_service_builder()
        return self._mutations

    def get_attachment_metadata_store(self):
        return self._mutation_service().get_attachment_metadata_store()

    def get_prep_snapshot(self):
        return self._prep_snapshot_getter()

    def attach_file_metadata(self, *, task_id: str, attachment):
        return self._mutation_service().attach_file_metadata(task_id=task_id, attachment=attachment)

    def delete_attachment(self, *, task_id: str, attachment_id: str):
        return self._mutation_service().delete_attachment(task_id=task_id, attachment_id=attachment_id)

    def cleanup_stale_attachments(self, *, ttl_seconds: int, delete_object):
        return self._mutation_service().cleanup_stale_attachments(
            ttl_seconds=ttl_seconds,
            delete_object=delete_object,
        )

    def get_response_cache_store(self):
        return self._response_cache_store


@dataclass(slots=True)
class SnapshotUpdateApi:
    """Snapshot update API exposed to runtime orchestration."""

    _update_runner: Callable[..., Any]

    def update(self, *, task_source: Any, force: bool = False):
        return self._update_runner(task_source=task_source, force=force)


__all__ = [
    "SnapshotAttachmentApi",
    "SnapshotQueryApi",
    "SnapshotReadApi",
    "SnapshotUpdateApi",
]

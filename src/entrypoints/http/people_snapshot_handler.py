"""Compatibility wrapper for the access-api-owned people snapshot handler."""

from src.contexts.access_api.internal.people_snapshot_handler import (
    PeopleSnapshotHandler,
    build_snapshot_engine,
    get_people_snapshot,
)

__all__ = [
    "PeopleSnapshotHandler",
    "build_snapshot_engine",
    "get_people_snapshot",
]

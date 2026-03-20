"""Compatibility wrapper for the snapshot context update runner."""

from src.contexts.snapshot.application.update_job import UpdateSnapshotJob, build_snapshot_engine

__all__ = ["UpdateSnapshotJob", "build_snapshot_engine"]

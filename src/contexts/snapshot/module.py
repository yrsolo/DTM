"""Local builder for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass

from src.snapshot_engine import build_snapshot_engine


@dataclass(frozen=True, slots=True)
class SnapshotModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "snapshot"

    def build_engine(self, ctx):
        return build_snapshot_engine(ctx)

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

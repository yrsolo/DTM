from __future__ import annotations

from src.app.context import AppContext
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
from src.snapshot_engine import build_snapshot_engine


class UpdateSnapshotJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        task_source = build_sheets_normalized_task_source(
            key_json=str(self._ctx.deps.get("key_json", "")),
            sheet_info_data=dict(self._ctx.deps.get("sheet_info", {})),
            cfg=self._ctx.cfg,
            dry_run=bool(cmd.payload.get("dry_run", False)),
        )
        result = build_snapshot_engine(self._ctx).update(
            task_source=task_source,
            force=bool(cmd.payload.get("force_refresh", False)),
        )
        return {
            "artifact": "update_snapshot",
            "status": "ok",
            "source_id": result.source_id,
            "source_hash": result.source_hash,
            "changed": bool(result.changed),
            "raw_written": bool(result.raw_written),
            "prep_written": bool(result.prep_written),
            "fetched_at_utc": result.fetched_at_utc.isoformat(),
        }

from __future__ import annotations

from src.app.context import AppContext
from src.observability import timed
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source
from src.snapshot_engine import build_snapshot_engine


class UpdateSnapshotJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        task_source = build_sheets_normalized_task_source(
            key_json=str(self._ctx.deps.get("key_json", "")),
            sheet_info_data=dict(self._ctx.deps.get("sheet_info", {})),
            cfg=self._ctx.cfg,
            dry_run=bool(cmd.payload.get("dry_run", False)),
        )
        with timed(metrics, "dtm.snapshot.update_duration_ms", {"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "snapshot", "operation": "update", "result": "finished"}):
            result = build_snapshot_engine(self._ctx).update(
                task_source=task_source,
                force=bool(cmd.payload.get("force_refresh", False)),
            )
        if metrics is not None:
            labels = {"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "snapshot", "operation": "update", "result": "success"}
            metrics.counter("dtm.snapshot.update_total", labels=labels)
            metrics.counter(
                "dtm.snapshot.changed_total" if bool(result.changed) else "dtm.snapshot.nochange_total",
                labels=labels,
            )
            for metric_name in (
                "dtm.snapshot.fetch_sheet_ms",
                "dtm.snapshot.normalize_ms",
                "dtm.snapshot.build_prep_ms",
                "dtm.snapshot.extra_load_ms",
                "dtm.snapshot.orphan_reconcile_ms",
                "dtm.snapshot.task_view_build_ms",
                "dtm.snapshot.prep_index_build_ms",
                "dtm.snapshot.write_raw_ms",
                "dtm.snapshot.write_prep_ms",
            ):
                timing_value = result.timings_ms.get(metric_name.removeprefix("dtm.snapshot."))
                if timing_value is not None:
                    metrics.timing(metric_name, float(timing_value), labels=labels)
        if logger is not None:
            logger.info(
                "snapshot_update_finished",
                source_id=result.source_id,
                changed=bool(result.changed),
                raw_written=bool(result.raw_written),
                prep_written=bool(result.prep_written),
                timings_ms=dict(result.timings_ms),
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
            "timings_ms": dict(result.timings_ms),
        }

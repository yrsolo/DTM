from __future__ import annotations

from time import perf_counter

from src.app.context import AppContext
from src.contexts.snapshot.application.capabilities import SnapshotUpdateCapability
from src.observability import timed
from src.observability.batching import (
    MetricsBatchCollector,
    add_flush_metrics,
    is_detailed_metrics_enabled,
)
from src.observability.buffered_metrics import managed_metrics_scope
from src.services.sources.sheets_normalized_source import build_sheets_normalized_task_source


def get_snapshot_capability(ctx):
    return SnapshotUpdateCapability(ctx)


class UpdateSnapshotJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        env_name = str(self._ctx.cfg.runtime.runtime.env_default)
        labels = {"env": env_name, "module": "snapshot", "operation": "update", "result": "success"}
        with managed_metrics_scope(metrics):
            collector = MetricsBatchCollector(metrics)
            wall_clock_started = perf_counter()
            task_source = build_sheets_normalized_task_source(
                key_json=str(self._ctx.deps.get("key_json", "")),
                sheet_info_data=dict(self._ctx.deps.get("sheet_info", {})),
                cfg=self._ctx.cfg,
                dry_run=bool(cmd.payload.get("dry_run", False)),
            )
            with timed(
                collector,
                "dtm.snapshot.update_duration_ms",
                {"env": env_name, "module": "snapshot", "operation": "update", "result": "finished"},
            ):
                result = get_snapshot_capability(self._ctx).update(
                    task_source=task_source,
                    force=bool(cmd.payload.get("force_refresh", False)),
                )
            collector.counter("dtm.snapshot.update_total", labels=labels)
            collector.counter(
                "dtm.snapshot.changed_total" if bool(result.changed) else "dtm.snapshot.nochange_total",
                labels=labels,
            )
            detailed_metrics_enabled = is_detailed_metrics_enabled(self._ctx)
            for metric_name in (
                "dtm.snapshot.fetch_sheet_ms",
                "dtm.snapshot.normalize_ms",
                "dtm.snapshot.build_prep_ms",
                "dtm.snapshot.write_raw_ms",
                "dtm.snapshot.write_prep_ms",
            ):
                timing_value = result.timings_ms.get(metric_name.removeprefix("dtm.snapshot."))
                if timing_value is not None:
                    collector.timing(metric_name, float(timing_value), labels=labels)
            if detailed_metrics_enabled:
                for metric_name in (
                    "dtm.snapshot.extra_load_ms",
                    "dtm.snapshot.orphan_reconcile_ms",
                    "dtm.snapshot.task_view_build_ms",
                    "dtm.snapshot.prep_index_build_ms",
                ):
                    timing_value = result.timings_ms.get(metric_name.removeprefix("dtm.snapshot."))
                    if timing_value is not None:
                        collector.timing(metric_name, float(timing_value), labels=labels)
            flush_report = collector.flush()
            post_collector = MetricsBatchCollector(metrics)
            add_flush_metrics(
                post_collector,
                env_name=env_name,
                module="snapshot",
                operation="update",
                report=flush_report,
            )
            wall_clock_ms = (perf_counter() - wall_clock_started) * 1000.0
            post_collector.timing("dtm.snapshot.job_wall_clock_ms", wall_clock_ms, labels=labels)
            post_collector.flush()
        if logger is not None:
            logger.info(
                "snapshot_update_finished",
                source_id=result.source_id,
                changed=bool(result.changed),
                raw_written=bool(result.raw_written),
                prep_written=bool(result.prep_written),
                timings_ms=dict(result.timings_ms),
                wall_clock_ms=round(wall_clock_ms, 2),
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
            "job_wall_clock_ms": float(round(wall_clock_ms, 3)),
        }


__all__ = ["UpdateSnapshotJob", "get_snapshot_capability"]

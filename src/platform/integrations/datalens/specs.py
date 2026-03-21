from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DataLensChartSpec:
    key: str
    name: str
    title: str
    description: str
    query: str
    x: int
    y: int
    w: int = 12
    h: int = 6


@dataclass(frozen=True, slots=True)
class DataLensDashboardSpec:
    name: str
    title: str
    description: str
    charts: tuple[DataLensChartSpec, ...]


def _env_filter(env_name: str) -> str:
    return f'env="{str(env_name or "").strip().lower() or "test"}",namespace="dtm",service_name="custom"'


def build_test_ops_dashboard_spec(env_name: str = "test") -> DataLensDashboardSpec:
    env_filter = _env_filter(env_name)
    charts = (
        DataLensChartSpec(
            key="snapshot_stage_timings",
            name="Snapshot Stage Timings",
            title="Snapshot Stage Timings",
            description="Breakdown of snapshot update stages.",
            query="\n".join(
                [
                    f'dtm.snapshot.fetch_sheet_ms{{{env_filter}}}',
                    f'dtm.snapshot.normalize_ms{{{env_filter}}}',
                    f'dtm.snapshot.build_prep_ms{{{env_filter}}}',
                    f'dtm.snapshot.write_raw_ms{{{env_filter}}}',
                    f'dtm.snapshot.write_prep_ms{{{env_filter}}}',
                ]
            ),
            x=0,
            y=0,
        ),
        DataLensChartSpec(
            key="snapshot_total_duration",
            name="Snapshot Total Duration",
            title="Snapshot Total Duration",
            description="Overall snapshot update duration.",
            query=f'dtm.snapshot.update_duration_ms{{{env_filter}}}',
            x=12,
            y=0,
        ),
        DataLensChartSpec(
            key="snapshot_outcomes",
            name="Snapshot Outcomes",
            title="Snapshot Outcomes",
            description="Update, changed and nochange counters.",
            query="\n".join(
                [
                    f'dtm.snapshot.update_total{{{env_filter}}}',
                    f'dtm.snapshot.changed_total{{{env_filter}}}',
                    f'dtm.snapshot.nochange_total{{{env_filter}}}',
                ]
            ),
            x=0,
            y=6,
        ),
        DataLensChartSpec(
            key="render_stage_timings",
            name="Render Stage Timings",
            title="Render Stage Timings",
            description="Timeline/designers build plan vs sheet write.",
            query="\n".join(
                [
                    f'dtm.render.build_plan_ms{{{env_filter}}}',
                    f'dtm.render.write_sheet_ms{{{env_filter}}}',
                ]
            ),
            x=12,
            y=6,
        ),
        DataLensChartSpec(
            key="render_total_duration",
            name="Render Total Duration",
            title="Render Total Duration",
            description="Overall render duration.",
            query=f'dtm.render.duration_ms{{{env_filter}}}',
            x=0,
            y=12,
        ),
        DataLensChartSpec(
            key="render_volume",
            name="Render Volume",
            title="Render Volume",
            description="Rendered rows and written cells.",
            query="\n".join(
                [
                    f'dtm.render.rows_rendered{{{env_filter}}}',
                    f'dtm.render.cells_written{{{env_filter}}}',
                ]
            ),
            x=12,
            y=12,
        ),
        DataLensChartSpec(
            key="api_latency",
            name="API Latency",
            title="API Latency",
            description="API duration time series.",
            query=f'dtm.api.duration_ms{{{env_filter}}}',
            x=0,
            y=18,
        ),
        DataLensChartSpec(
            key="api_throughput",
            name="API Throughput",
            title="API Throughput",
            description="API request throughput.",
            query=f'dtm.api.requests_total{{{env_filter}}}',
            x=12,
            y=18,
        ),
        DataLensChartSpec(
            key="worker_reliability",
            name="Worker Reliability",
            title="Worker Reliability",
            description="Command counts, duration, failures and retries.",
            query="\n".join(
                [
                    f'dtm.worker.commands_total{{{env_filter}}}',
                    f'dtm.worker.command_duration_ms{{{env_filter}}}',
                    f'dtm.worker.command_failures_total{{{env_filter}}}',
                    f'dtm.worker.command_retries_total{{{env_filter}}}',
                ]
            ),
            x=0,
            y=24,
        ),
        DataLensChartSpec(
            key="notify_runtime",
            name="Notify Runtime",
            title="Notify Runtime",
            description="Notify total duration, messages sent, tasks selected.",
            query="\n".join(
                [
                    f'dtm.notify.duration_ms{{{env_filter}}}',
                    f'dtm.notify.messages_sent{{{env_filter}}}',
                    f'dtm.notify.tasks_selected{{{env_filter}}}',
                ]
            ),
            x=12,
            y=24,
        ),
        DataLensChartSpec(
            key="telegram_intake",
            name="Telegram Intake",
            title="Telegram Intake",
            description="Webhook accept/reject, enqueue latency and commands.",
            query="\n".join(
                [
                    f'dtm.telegram.accepted_total{{{env_filter}}}',
                    f'dtm.telegram.rejected_total{{{env_filter}}}',
                    f'dtm.telegram.enqueue_ms{{{env_filter}}}',
                    f'dtm.telegram.command_total{{{env_filter}}}',
                ]
            ),
            x=0,
            y=30,
        ),
    )
    return DataLensDashboardSpec(
        name="DTM Test Ops",
        title="DTM Test Ops",
        description="Operator dashboard for DTM test contour over Yandex Monitoring metrics.",
        charts=charts,
    )

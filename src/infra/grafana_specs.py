from __future__ import annotations

from typing import Any


def _prom_metric(metric_name: str) -> str:
    return str(metric_name or "").strip().lower().replace(".", "_")


def _expr(metric_name: str, env_name: str, extra_selector: str = "") -> str:
    base = f'{{env="{env_name}",namespace="dtm",service="dtm"'
    if extra_selector:
        base += f",{extra_selector}"
    base += "}"
    return f"{_prom_metric(metric_name)}{base}"


def _datasource_ref(*, datasource_uid: str = "", datasource_name: str = "") -> dict[str, str] | str | None:
    uid_value = str(datasource_uid or "").strip()
    if uid_value:
        return {"type": "prometheus", "uid": uid_value}
    name_value = str(datasource_name or "").strip()
    if name_value:
        return name_value
    return None


def build_test_grafana_dashboard(
    env_name: str = "test",
    *,
    datasource_uid: str = "",
    datasource_name: str = "",
) -> dict[str, Any]:
    datasource = _datasource_ref(datasource_uid=datasource_uid, datasource_name=datasource_name)
    panels = [
        {
            "id": 1,
            "title": "Snapshot Stage Timings",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {"expr": _expr("dtm.snapshot.fetch_sheet_ms", env_name), "legendFormat": "fetch_sheet_ms"},
                {"expr": _expr("dtm.snapshot.normalize_ms", env_name), "legendFormat": "normalize_ms"},
                {"expr": _expr("dtm.snapshot.build_prep_ms", env_name), "legendFormat": "build_prep_ms"},
                {"expr": _expr("dtm.snapshot.write_raw_ms", env_name), "legendFormat": "write_raw_ms"},
                {"expr": _expr("dtm.snapshot.write_prep_ms", env_name), "legendFormat": "write_prep_ms"},
            ],
        },
        {
            "id": 2,
            "title": "Snapshot Total Duration",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [{"expr": _expr("dtm.snapshot.update_duration_ms", env_name), "legendFormat": "total"}],
        },
        {
            "id": 3,
            "title": "Snapshot Outcomes",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {"expr": _expr("dtm.snapshot.update_total", env_name), "legendFormat": "update_total"},
                {"expr": _expr("dtm.snapshot.changed_total", env_name), "legendFormat": "changed_total"},
                {"expr": _expr("dtm.snapshot.nochange_total", env_name), "legendFormat": "nochange_total"},
            ],
        },
        {
            "id": 4,
            "title": "Render Stage Timings",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {
                    "expr": _expr("dtm.render.build_plan_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} build_plan_ms",
                },
                {
                    "expr": _expr("dtm.render.write_sheet_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} write_sheet_ms",
                },
            ],
        },
        {
            "id": 5,
            "title": "Render Total Duration",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {
                    "expr": _expr("dtm.render.duration_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} total",
                }
            ],
        },
        {
            "id": 6,
            "title": "Render Volume",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {
                    "expr": _expr("dtm.render.rows_rendered", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} rows_rendered",
                },
                {
                    "expr": _expr("dtm.render.cells_written", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} cells_written",
                },
            ],
        },
        {
            "id": 7,
            "title": "API Latency",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [{"expr": _expr("dtm.api.duration_ms", env_name), "legendFormat": "{{operation}}"}],
        },
        {
            "id": 8,
            "title": "API Throughput",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [{"expr": _expr("dtm.api.requests_total", env_name), "legendFormat": "{{operation}}"}],
        },
        {
            "id": 9,
            "title": "Worker Reliability",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {"expr": _expr("dtm.worker.commands_total", env_name), "legendFormat": "commands_total"},
                {"expr": _expr("dtm.worker.command_duration_ms", env_name), "legendFormat": "command_duration_ms"},
                {"expr": _expr("dtm.worker.command_failures_total", env_name), "legendFormat": "command_failures_total"},
                {"expr": _expr("dtm.worker.command_retries_total", env_name), "legendFormat": "command_retries_total"},
            ],
        },
        {
            "id": 10,
            "title": "Notify Runtime",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {"expr": _expr("dtm.notify.duration_ms", env_name), "legendFormat": "duration_ms"},
                {"expr": _expr("dtm.notify.messages_sent", env_name), "legendFormat": "messages_sent"},
                {"expr": _expr("dtm.notify.tasks_selected", env_name), "legendFormat": "tasks_selected"},
            ],
        },
        {
            "id": 11,
            "title": "Telegram Intake",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 40, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": [
                {"expr": _expr("dtm.telegram.accepted_total", env_name), "legendFormat": "accepted_total"},
                {"expr": _expr("dtm.telegram.rejected_total", env_name), "legendFormat": "rejected_total"},
                {"expr": _expr("dtm.telegram.enqueue_ms", env_name), "legendFormat": "enqueue_ms"},
                {"expr": _expr("dtm.telegram.command_total", env_name), "legendFormat": "command_total"},
            ],
        },
    ]
    return {
        "title": "DTM Test Ops",
        "uid": "dtm-test-ops",
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "30s",
        "panels": panels,
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "time": {"from": "now-24h", "to": "now"},
        "templating": {"list": []},
        "tags": ["dtm", "ops", env_name],
    }

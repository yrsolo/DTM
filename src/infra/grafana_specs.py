from __future__ import annotations

from typing import Any


def _with_ref_ids(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, target in enumerate(targets):
        target_copy = dict(target)
        target_copy["refId"] = chr(ord("A") + index)
        result.append(target_copy)
    return result


def _prom_metric(metric_name: str) -> str:
    return str(metric_name or "").strip().lower().replace(".", "_")


def _expr(metric_name: str, env_name: str, extra_selector: str = "") -> str:
    base = f'{{env="{env_name}",namespace="dtm",service="dtm"'
    if extra_selector:
        base += f",{extra_selector}"
    base += "}"
    return f"{_prom_metric(metric_name)}{base}"


def _max_expr(metric_name: str, env_name: str, extra_selector: str = "") -> str:
    return f"max({_expr(metric_name, env_name, extra_selector)})"


def _datasource_ref(*, datasource_uid: str = "", datasource_name: str = "") -> dict[str, str] | str | None:
    uid_value = str(datasource_uid or "").strip()
    if uid_value:
        return {"type": "prometheus", "uid": uid_value}
    name_value = str(datasource_name or "").strip()
    if name_value:
        return name_value
    return None


def _stat_panel(
    *,
    panel_id: int,
    title: str,
    expr: str,
    datasource: dict[str, str] | str | None,
    x: int,
    y: int,
    w: int = 4,
    h: int = 4,
) -> dict[str, Any]:
    return {
        "id": panel_id,
        "title": title,
        "type": "stat",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource,
        "targets": _with_ref_ids([{"expr": expr, "legendFormat": title}]),
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "orientation": "auto",
            "textMode": "value",
            "colorMode": "none",
            "graphMode": "none",
            "justifyMode": "auto",
        },
    }


def build_test_grafana_dashboard(
    env_name: str = "test",
    *,
    datasource_uid: str = "",
    datasource_name: str = "",
) -> dict[str, Any]:
    datasource = _datasource_ref(datasource_uid=datasource_uid, datasource_name=datasource_name)
    panels = [
        _stat_panel(panel_id=100, title="Snapshot Fetch Last", expr=_expr("dtm.snapshot.fetch_sheet_last_ms", env_name), datasource=datasource, x=0, y=0),
        _stat_panel(panel_id=101, title="Snapshot Fetch Avg5", expr=_expr("dtm.snapshot.fetch_sheet_last5_avg_ms", env_name), datasource=datasource, x=4, y=0),
        _stat_panel(panel_id=102, title="Normalize Last", expr=_expr("dtm.snapshot.normalize_last_ms", env_name), datasource=datasource, x=8, y=0),
        _stat_panel(panel_id=103, title="Normalize Avg5", expr=_expr("dtm.snapshot.normalize_last5_avg_ms", env_name), datasource=datasource, x=12, y=0),
        _stat_panel(panel_id=104, title="Build Prep Last", expr=_expr("dtm.snapshot.build_prep_last_ms", env_name), datasource=datasource, x=16, y=0),
        _stat_panel(panel_id=105, title="Build Prep Avg5", expr=_expr("dtm.snapshot.build_prep_last5_avg_ms", env_name), datasource=datasource, x=20, y=0),
        _stat_panel(panel_id=106, title="Render Plan Last", expr=_max_expr("dtm.render.build_plan_last_ms", env_name, 'operation=~".+"'), datasource=datasource, x=0, y=4),
        _stat_panel(panel_id=107, title="Render Plan Avg5", expr=_max_expr("dtm.render.build_plan_last5_avg_ms", env_name, 'operation=~".+"'), datasource=datasource, x=4, y=4),
        _stat_panel(panel_id=108, title="Write Sheet Last", expr=_max_expr("dtm.render.write_sheet_last_ms", env_name, 'operation=~".+"'), datasource=datasource, x=8, y=4),
        _stat_panel(panel_id=109, title="Write Sheet Avg5", expr=_max_expr("dtm.render.write_sheet_last5_avg_ms", env_name, 'operation=~".+"'), datasource=datasource, x=12, y=4),
        _stat_panel(panel_id=110, title="Render Total Last", expr=_max_expr("dtm.render.duration_last_ms", env_name, 'operation=~".+"'), datasource=datasource, x=16, y=4),
        _stat_panel(panel_id=111, title="Render Total Avg5", expr=_max_expr("dtm.render.duration_last5_avg_ms", env_name, 'operation=~".+"'), datasource=datasource, x=20, y=4),
        {
            "id": 1,
            "title": "Snapshot Stage Timings",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {"expr": _expr("dtm.snapshot.fetch_sheet_ms", env_name), "legendFormat": "fetch_sheet_ms"},
                {"expr": _expr("dtm.snapshot.normalize_ms", env_name), "legendFormat": "normalize_ms"},
                {"expr": _expr("dtm.snapshot.build_prep_ms", env_name), "legendFormat": "build_prep_ms"},
                {"expr": _expr("dtm.snapshot.write_raw_ms", env_name), "legendFormat": "write_raw_ms"},
                {"expr": _expr("dtm.snapshot.write_prep_ms", env_name), "legendFormat": "write_prep_ms"},
            ]),
        },
        {
            "id": 2,
            "title": "Snapshot Total Duration",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids(
                [{"expr": _expr("dtm.snapshot.update_duration_ms", env_name), "legendFormat": "total"}]
            ),
        },
        {
            "id": 3,
            "title": "Snapshot Outcomes",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {"expr": _expr("dtm.snapshot.update_total", env_name), "legendFormat": "update_total"},
                {"expr": _expr("dtm.snapshot.changed_total", env_name), "legendFormat": "changed_total"},
                {"expr": _expr("dtm.snapshot.nochange_total", env_name), "legendFormat": "nochange_total"},
            ]),
        },
        {
            "id": 4,
            "title": "Render Stage Timings",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {
                    "expr": _expr("dtm.render.build_plan_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} build_plan_ms",
                },
                {
                    "expr": _expr("dtm.render.write_sheet_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} write_sheet_ms",
                },
            ]),
        },
        {
            "id": 5,
            "title": "Render Total Duration",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {
                    "expr": _expr("dtm.render.duration_ms", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} total",
                }
            ]),
        },
        {
            "id": 6,
            "title": "Render Volume",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {
                    "expr": _expr("dtm.render.rows_rendered", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} rows_rendered",
                },
                {
                    "expr": _expr("dtm.render.cells_written", env_name, 'operation=~".+"'),
                    "legendFormat": "{{operation}} cells_written",
                },
            ]),
        },
        {
            "id": 7,
            "title": "API Latency",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([{"expr": _expr("dtm.api.duration_ms", env_name), "legendFormat": "{{operation}}"}]),
        },
        {
            "id": 8,
            "title": "API Throughput",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([{"expr": _expr("dtm.api.requests_total", env_name), "legendFormat": "{{operation}}"}]),
        },
        {
            "id": 9,
            "title": "Worker Reliability",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 40, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {"expr": _expr("dtm.worker.commands_total", env_name), "legendFormat": "commands_total"},
                {"expr": _expr("dtm.worker.command_duration_ms", env_name), "legendFormat": "command_duration_ms"},
                {"expr": _expr("dtm.worker.command_failures_total", env_name), "legendFormat": "command_failures_total"},
                {"expr": _expr("dtm.worker.command_retries_total", env_name), "legendFormat": "command_retries_total"},
            ]),
        },
        {
            "id": 10,
            "title": "Notify Runtime",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 40, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {"expr": _expr("dtm.notify.duration_ms", env_name), "legendFormat": "duration_ms"},
                {"expr": _expr("dtm.notify.messages_sent", env_name), "legendFormat": "messages_sent"},
                {"expr": _expr("dtm.notify.tasks_selected", env_name), "legendFormat": "tasks_selected"},
            ]),
        },
        {
            "id": 11,
            "title": "Telegram Intake",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 48, "w": 12, "h": 8},
            "datasource": datasource,
            "targets": _with_ref_ids([
                {"expr": _expr("dtm.telegram.accepted_total", env_name), "legendFormat": "accepted_total"},
                {"expr": _expr("dtm.telegram.rejected_total", env_name), "legendFormat": "rejected_total"},
                {"expr": _expr("dtm.telegram.enqueue_ms", env_name), "legendFormat": "enqueue_ms"},
                {"expr": _expr("dtm.telegram.command_total", env_name), "legendFormat": "command_total"},
            ]),
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

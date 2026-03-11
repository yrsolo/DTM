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


def _last_expr(metric_name: str, env_name: str, extra_selector: str = "", window: str = "7d") -> str:
    return f"last_over_time({_expr(metric_name, env_name, extra_selector)}[{window}])"


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


def _avg5_stat_panel(
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
        "targets": _with_ref_ids([{"expr": expr, "legendFormat": title, "instant": False, "range": True}]),
        "transformations": [
            {"id": "seriesToRows", "options": {}},
            {"id": "sortBy", "options": {"fields": {}, "sort": [{"field": "Time", "desc": True}]}},
            {"id": "limit", "options": {"limit": 5}},
            {"id": "reduce", "options": {"reducers": ["mean"]}},
        ],
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "/Value|Mean/", "values": False},
            "orientation": "auto",
            "textMode": "value",
            "colorMode": "none",
            "graphMode": "none",
            "justifyMode": "auto",
        },
    }


def _timeseries_field_config() -> dict[str, Any]:
    return {
        "defaults": {
            "custom": {
                "drawStyle": "line",
                "lineInterpolation": "linear",
                "showPoints": "never",
                "spanNulls": False,
            }
        },
        "overrides": [],
    }


def build_test_grafana_dashboard(
    env_name: str = "test",
    *,
    datasource_uid: str = "",
    datasource_name: str = "",
) -> dict[str, Any]:
    datasource = _datasource_ref(datasource_uid=datasource_uid, datasource_name=datasource_name)
    panels = [
        _stat_panel(panel_id=100, title="Snapshot Fetch Last", expr=_last_expr("dtm.snapshot.fetch_sheet_ms", env_name), datasource=datasource, x=0, y=0),
        _avg5_stat_panel(panel_id=101, title="Snapshot Fetch Avg5", expr=_expr("dtm.snapshot.fetch_sheet_ms", env_name), datasource=datasource, x=4, y=0),
        _stat_panel(panel_id=102, title="Normalize Last", expr=_last_expr("dtm.snapshot.normalize_ms", env_name), datasource=datasource, x=8, y=0),
        _avg5_stat_panel(panel_id=103, title="Normalize Avg5", expr=_expr("dtm.snapshot.normalize_ms", env_name), datasource=datasource, x=12, y=0),
        _stat_panel(panel_id=104, title="Build Prep Last", expr=_last_expr("dtm.snapshot.build_prep_ms", env_name), datasource=datasource, x=16, y=0),
        _avg5_stat_panel(panel_id=105, title="Build Prep Avg5", expr=_expr("dtm.snapshot.build_prep_ms", env_name), datasource=datasource, x=20, y=0),
        _stat_panel(panel_id=106, title="Write Raw Last", expr=_last_expr("dtm.snapshot.write_raw_ms", env_name), datasource=datasource, x=0, y=4),
        _avg5_stat_panel(panel_id=107, title="Write Raw Avg5", expr=_expr("dtm.snapshot.write_raw_ms", env_name), datasource=datasource, x=4, y=4),
        _stat_panel(panel_id=108, title="Write Prep Last", expr=_last_expr("dtm.snapshot.write_prep_ms", env_name), datasource=datasource, x=8, y=4),
        _avg5_stat_panel(panel_id=109, title="Write Prep Avg5", expr=_expr("dtm.snapshot.write_prep_ms", env_name), datasource=datasource, x=12, y=4),
        _stat_panel(panel_id=110, title="Extra Load Last", expr=_last_expr("dtm.snapshot.extra_load_ms", env_name), datasource=datasource, x=16, y=4),
        _avg5_stat_panel(panel_id=111, title="Extra Load Avg5", expr=_expr("dtm.snapshot.extra_load_ms", env_name), datasource=datasource, x=20, y=4),
        _stat_panel(panel_id=112, title="Task View Last", expr=_last_expr("dtm.snapshot.task_view_build_ms", env_name), datasource=datasource, x=0, y=8),
        _avg5_stat_panel(panel_id=113, title="Task View Avg5", expr=_expr("dtm.snapshot.task_view_build_ms", env_name), datasource=datasource, x=4, y=8),
        _stat_panel(panel_id=114, title="Prep Index Last", expr=_last_expr("dtm.snapshot.prep_index_build_ms", env_name), datasource=datasource, x=8, y=8),
        _avg5_stat_panel(panel_id=115, title="Prep Index Avg5", expr=_expr("dtm.snapshot.prep_index_build_ms", env_name), datasource=datasource, x=12, y=8),
        _stat_panel(panel_id=116, title="Timeline Plan Last", expr=_last_expr("dtm.render.build_plan_ms", env_name, 'operation="timeline"'), datasource=datasource, x=0, y=12),
        _avg5_stat_panel(panel_id=117, title="Timeline Plan Avg5", expr=_expr("dtm.render.build_plan_ms", env_name, 'operation="timeline"'), datasource=datasource, x=4, y=12),
        _stat_panel(panel_id=118, title="Timeline Write Last", expr=_last_expr("dtm.render.write_sheet_ms", env_name, 'operation="timeline"'), datasource=datasource, x=8, y=12),
        _avg5_stat_panel(panel_id=119, title="Timeline Write Avg5", expr=_expr("dtm.render.write_sheet_ms", env_name, 'operation="timeline"'), datasource=datasource, x=12, y=12),
        _stat_panel(panel_id=120, title="Timeline Total Last", expr=_last_expr("dtm.render.duration_ms", env_name, 'operation="timeline"'), datasource=datasource, x=16, y=12),
        _avg5_stat_panel(panel_id=121, title="Timeline Total Avg5", expr=_expr("dtm.render.duration_ms", env_name, 'operation="timeline"'), datasource=datasource, x=20, y=12),
        _stat_panel(panel_id=122, title="Designers Plan Last", expr=_last_expr("dtm.render.build_plan_ms", env_name, 'operation="designers"'), datasource=datasource, x=0, y=16),
        _avg5_stat_panel(panel_id=123, title="Designers Plan Avg5", expr=_expr("dtm.render.build_plan_ms", env_name, 'operation="designers"'), datasource=datasource, x=4, y=16),
        _stat_panel(panel_id=124, title="Designers Write Last", expr=_last_expr("dtm.render.write_sheet_ms", env_name, 'operation="designers"'), datasource=datasource, x=8, y=16),
        _avg5_stat_panel(panel_id=125, title="Designers Write Avg5", expr=_expr("dtm.render.write_sheet_ms", env_name, 'operation="designers"'), datasource=datasource, x=12, y=16),
        _stat_panel(panel_id=126, title="Designers Total Last", expr=_last_expr("dtm.render.duration_ms", env_name, 'operation="designers"'), datasource=datasource, x=16, y=16),
        _avg5_stat_panel(panel_id=127, title="Designers Total Avg5", expr=_expr("dtm.render.duration_ms", env_name, 'operation="designers"'), datasource=datasource, x=20, y=16),
        _stat_panel(panel_id=128, title="Snapshot Business Duration", expr=_last_expr("dtm.snapshot.update_duration_ms", env_name), datasource=datasource, x=0, y=20, w=6),
        _stat_panel(panel_id=129, title="Snapshot Job Wall Clock", expr=_last_expr("dtm.snapshot.job_wall_clock_ms", env_name), datasource=datasource, x=6, y=20, w=6),
        _stat_panel(panel_id=130, title="Worker Wall Clock", expr=_last_expr("dtm.worker.wall_clock_ms", env_name, 'operation="update_snapshot"'), datasource=datasource, x=12, y=20, w=6),
        _stat_panel(panel_id=131, title="Metrics Flush Total", expr=_last_expr("dtm.metrics.flush_duration_ms", env_name, 'module="snapshot",operation="update",backend="combined"'), datasource=datasource, x=18, y=20, w=6),
        {
            "id": 1,
            "title": "Snapshot Stage Timings",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 12, "y": 24, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
            "targets": _with_ref_ids(
                [{"expr": _expr("dtm.snapshot.update_duration_ms", env_name), "legendFormat": "total"}]
            ),
        },
        {
            "id": 3,
            "title": "Snapshot Outcomes",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 12, "y": 32, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 0, "y": 40, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 12, "y": 40, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 0, "y": 48, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
            "targets": _with_ref_ids([{"expr": _expr("dtm.api.duration_ms", env_name), "legendFormat": "{{operation}}"}]),
        },
        {
            "id": 8,
            "title": "API Throughput",
            "type": "timeseries",
            "gridPos": {"x": 12, "y": 48, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
            "targets": _with_ref_ids([{"expr": _expr("dtm.api.requests_total", env_name), "legendFormat": "{{operation}}"}]),
        },
        {
            "id": 9,
            "title": "Worker Reliability",
            "type": "timeseries",
            "gridPos": {"x": 0, "y": 56, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 12, "y": 56, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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
            "gridPos": {"x": 0, "y": 64, "w": 12, "h": 8},
            "datasource": datasource,
            "fieldConfig": _timeseries_field_config(),
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

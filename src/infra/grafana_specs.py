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


def _timeseries_panel(
    *,
    panel_id: int,
    title: str,
    targets: list[dict[str, Any]],
    datasource: dict[str, str] | str | None,
    x: int,
    y: int,
    w: int = 6,
    h: int = 8,
) -> dict[str, Any]:
    return {
        "id": panel_id,
        "title": title,
        "type": "timeseries",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource,
        "fieldConfig": _timeseries_field_config(),
        "targets": _with_ref_ids(targets),
    }


def build_test_grafana_dashboard(
    env_name: str = "test",
    *,
    datasource_uid: str = "",
    datasource_name: str = "",
) -> dict[str, Any]:
    datasource = _datasource_ref(datasource_uid=datasource_uid, datasource_name=datasource_name)
    stat_w = 2
    stat_h = 2
    stat_columns = 12
    stat_specs: list[tuple[str, int, str, str]] = [
        ("last", 100, "Snapshot Fetch Last", _last_expr("dtm.snapshot.fetch_sheet_ms", env_name)),
        ("avg", 101, "Snapshot Fetch Avg5", _expr("dtm.snapshot.fetch_sheet_ms", env_name)),
        ("last", 102, "Normalize Last", _last_expr("dtm.snapshot.normalize_ms", env_name)),
        ("avg", 103, "Normalize Avg5", _expr("dtm.snapshot.normalize_ms", env_name)),
        ("last", 104, "Build Prep Last", _last_expr("dtm.snapshot.build_prep_ms", env_name)),
        ("avg", 105, "Build Prep Avg5", _expr("dtm.snapshot.build_prep_ms", env_name)),
        ("last", 106, "Write Raw Last", _last_expr("dtm.snapshot.write_raw_ms", env_name)),
        ("avg", 107, "Write Raw Avg5", _expr("dtm.snapshot.write_raw_ms", env_name)),
        ("last", 108, "Write Prep Last", _last_expr("dtm.snapshot.write_prep_ms", env_name)),
        ("avg", 109, "Write Prep Avg5", _expr("dtm.snapshot.write_prep_ms", env_name)),
        ("last", 110, "Extra Load Last", _last_expr("dtm.snapshot.extra_load_ms", env_name)),
        ("avg", 111, "Extra Load Avg5", _expr("dtm.snapshot.extra_load_ms", env_name)),
        ("last", 112, "Orphan Reconcile Last", _last_expr("dtm.snapshot.orphan_reconcile_ms", env_name)),
        ("avg", 113, "Orphan Reconcile Avg5", _expr("dtm.snapshot.orphan_reconcile_ms", env_name)),
        ("last", 114, "Task View Last", _last_expr("dtm.snapshot.task_view_build_ms", env_name)),
        ("avg", 115, "Task View Avg5", _expr("dtm.snapshot.task_view_build_ms", env_name)),
        ("last", 116, "Prep Index Last", _last_expr("dtm.snapshot.prep_index_build_ms", env_name)),
        ("avg", 117, "Prep Index Avg5", _expr("dtm.snapshot.prep_index_build_ms", env_name)),
        ("last", 118, "Timeline Plan Last", _last_expr("dtm.render.build_plan_ms", env_name, 'operation="timeline"')),
        ("avg", 119, "Timeline Plan Avg5", _expr("dtm.render.build_plan_ms", env_name, 'operation="timeline"')),
        ("last", 120, "Timeline Write Last", _last_expr("dtm.render.write_sheet_ms", env_name, 'operation="timeline"')),
        ("avg", 121, "Timeline Write Avg5", _expr("dtm.render.write_sheet_ms", env_name, 'operation="timeline"')),
        ("last", 122, "Timeline Total Last", _last_expr("dtm.render.duration_ms", env_name, 'operation="timeline"')),
        ("avg", 123, "Timeline Total Avg5", _expr("dtm.render.duration_ms", env_name, 'operation="timeline"')),
        ("last", 124, "Timeline Wall Clock Last", _last_expr("dtm.render.job_wall_clock_ms", env_name, 'operation="timeline"')),
        ("avg", 125, "Timeline Wall Clock Avg5", _expr("dtm.render.job_wall_clock_ms", env_name, 'operation="timeline"')),
        ("last", 126, "Designers Plan Last", _last_expr("dtm.render.build_plan_ms", env_name, 'operation="designers"')),
        ("avg", 127, "Designers Plan Avg5", _expr("dtm.render.build_plan_ms", env_name, 'operation="designers"')),
        ("last", 128, "Designers Write Last", _last_expr("dtm.render.write_sheet_ms", env_name, 'operation="designers"')),
        ("avg", 129, "Designers Write Avg5", _expr("dtm.render.write_sheet_ms", env_name, 'operation="designers"')),
        ("last", 130, "Designers Total Last", _last_expr("dtm.render.duration_ms", env_name, 'operation="designers"')),
        ("avg", 131, "Designers Total Avg5", _expr("dtm.render.duration_ms", env_name, 'operation="designers"')),
        ("last", 132, "Designers Wall Clock Last", _last_expr("dtm.render.job_wall_clock_ms", env_name, 'operation="designers"')),
        ("avg", 133, "Designers Wall Clock Avg5", _expr("dtm.render.job_wall_clock_ms", env_name, 'operation="designers"')),
        ("last", 134, "Snapshot Business Duration", _last_expr("dtm.snapshot.update_duration_ms", env_name)),
        ("avg", 135, "Snapshot Business Avg5", _expr("dtm.snapshot.update_duration_ms", env_name)),
        ("last", 136, "Snapshot Job Wall Clock", _last_expr("dtm.snapshot.job_wall_clock_ms", env_name)),
        ("avg", 137, "Snapshot Wall Clock Avg5", _expr("dtm.snapshot.job_wall_clock_ms", env_name)),
        ("last", 138, "Worker Wall Clock", _last_expr("dtm.worker.wall_clock_ms", env_name, 'operation="update_snapshot"')),
        ("avg", 139, "Worker Wall Avg5", _expr("dtm.worker.wall_clock_ms", env_name, 'operation="update_snapshot"')),
        ("last", 140, "Metrics Flush Total", _last_expr("dtm.metrics.flush_duration_ms", env_name, 'module="snapshot",operation="update",backend="combined"')),
        ("avg", 141, "Metrics Flush Avg5", _expr("dtm.metrics.flush_duration_ms", env_name, 'module="snapshot",operation="update",backend="combined"')),
        ("last", 142, "API Latency Last", _last_expr("dtm.api.duration_ms", env_name)),
        ("avg", 143, "API Latency Avg5", _expr("dtm.api.duration_ms", env_name)),
        ("last", 144, "API Size Last", _last_expr("dtm.api.response_size_bytes", env_name)),
        ("avg", 145, "API Size Avg5", _expr("dtm.api.response_size_bytes", env_name)),
        ("last", 146, "Info Summary Last", _last_expr("dtm.info.summary.ms", env_name)),
        ("avg", 147, "Info Summary Avg5", _expr("dtm.info.summary.ms", env_name)),
        ("last", 148, "Info Detail Last", _last_expr("dtm.info.detail.ms", env_name)),
        ("avg", 149, "Info Detail Avg5", _expr("dtm.info.detail.ms", env_name)),
        ("last", 150, "Notify Duration Last", _last_expr("dtm.notify.duration_ms", env_name)),
        ("avg", 151, "Notify Duration Avg5", _expr("dtm.notify.duration_ms", env_name)),
        ("last", 152, "Telegram Enqueue Last", _last_expr("dtm.telegram.enqueue_ms", env_name)),
        ("avg", 153, "Telegram Enqueue Avg5", _expr("dtm.telegram.enqueue_ms", env_name)),
    ]
    panels: list[dict[str, Any]] = []
    for index, (kind, panel_id, title, expr) in enumerate(stat_specs):
        x = (index % stat_columns) * stat_w
        y = (index // stat_columns) * stat_h
        if kind == "avg":
            panels.append(
                _avg5_stat_panel(
                    panel_id=panel_id,
                    title=title,
                    expr=expr,
                    datasource=datasource,
                    x=x,
                    y=y,
                    w=stat_w,
                    h=stat_h,
                )
            )
        else:
            panels.append(
                _stat_panel(
                    panel_id=panel_id,
                    title=title,
                    expr=expr,
                    datasource=datasource,
                    x=x,
                    y=y,
                    w=stat_w,
                    h=stat_h,
                )
            )

    timeseries_y = ((len(stat_specs) + stat_columns - 1) // stat_columns) * stat_h
    timeseries_specs = [
        (
            1,
            "Snapshot Stage Timings",
            [
                {"expr": _expr("dtm.snapshot.fetch_sheet_ms", env_name), "legendFormat": "fetch_sheet_ms"},
                {"expr": _expr("dtm.snapshot.normalize_ms", env_name), "legendFormat": "normalize_ms"},
                {"expr": _expr("dtm.snapshot.build_prep_ms", env_name), "legendFormat": "build_prep_ms"},
                {"expr": _expr("dtm.snapshot.extra_load_ms", env_name), "legendFormat": "extra_load_ms"},
                {"expr": _expr("dtm.snapshot.orphan_reconcile_ms", env_name), "legendFormat": "orphan_reconcile_ms"},
                {"expr": _expr("dtm.snapshot.task_view_build_ms", env_name), "legendFormat": "task_view_build_ms"},
                {"expr": _expr("dtm.snapshot.prep_index_build_ms", env_name), "legendFormat": "prep_index_build_ms"},
                {"expr": _expr("dtm.snapshot.write_raw_ms", env_name), "legendFormat": "write_raw_ms"},
                {"expr": _expr("dtm.snapshot.write_prep_ms", env_name), "legendFormat": "write_prep_ms"},
            ],
        ),
        (
            2,
            "Snapshot Duration and Flush",
            [
                {"expr": _expr("dtm.snapshot.update_duration_ms", env_name), "legendFormat": "business_duration_ms"},
                {"expr": _expr("dtm.snapshot.job_wall_clock_ms", env_name), "legendFormat": "job_wall_clock_ms"},
                {
                    "expr": _expr("dtm.metrics.flush_duration_ms", env_name, 'module="snapshot",operation="update",backend="combined"'),
                    "legendFormat": "flush_duration_ms",
                },
            ],
        ),
        (
            3,
            "Snapshot Outcomes",
            [
                {"expr": _expr("dtm.snapshot.update_total", env_name), "legendFormat": "update_total"},
                {"expr": _expr("dtm.snapshot.changed_total", env_name), "legendFormat": "changed_total"},
                {"expr": _expr("dtm.snapshot.nochange_total", env_name), "legendFormat": "nochange_total"},
            ],
        ),
        (
            4,
            "Render Stage Timings",
            [
                {"expr": _expr("dtm.render.build_plan_ms", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} build_plan_ms"},
                {"expr": _expr("dtm.render.write_sheet_ms", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} write_sheet_ms"},
            ],
        ),
        (
            5,
            "Render Total and Wall Clock",
            [
                {"expr": _expr("dtm.render.duration_ms", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} duration_ms"},
                {"expr": _expr("dtm.render.job_wall_clock_ms", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} wall_clock_ms"},
            ],
        ),
        (
            6,
            "Render Volume and Runs",
            [
                {"expr": _expr("dtm.render.total", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} total"},
                {"expr": _expr("dtm.render.rows_rendered", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} rows_rendered"},
                {"expr": _expr("dtm.render.cells_written", env_name, 'operation=~".+"'), "legendFormat": "{{operation}} cells_written"},
            ],
        ),
        (
            7,
            "API and Info Latency",
            [
                {"expr": _expr("dtm.api.duration_ms", env_name), "legendFormat": "{{operation}} api_duration_ms"},
                {"expr": _expr("dtm.info.summary.ms", env_name), "legendFormat": "info.summary.ms"},
                {"expr": _expr("dtm.info.detail.ms", env_name), "legendFormat": "info.detail.ms"},
            ],
        ),
        (
            8,
            "API Size and Throughput",
            [
                {"expr": _expr("dtm.api.requests_total", env_name), "legendFormat": "{{operation}} requests_total"},
                {"expr": _expr("dtm.api.response_size_bytes", env_name), "legendFormat": "{{operation}} response_size_bytes"},
            ],
        ),
        (
            9,
            "Frontend Stage Breakdown",
            [
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",stage=~".+"'),
                    "legendFormat": "{{route}} {{access_mode}} {{cache_result}} {{stage}}",
                },
            ],
        ),
        (
            10,
            "Direct API Outer Breakdown",
            [
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage=~".+"'),
                    "legendFormat": "{{stage}}",
                },
            ],
        ),
        (
            11,
            "Direct API Outer vs Inner",
            [
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage="function_total"'),
                    "legendFormat": "function_total",
                },
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage="router_precheck_total"'),
                    "legendFormat": "router_precheck_total",
                },
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage="router_handler_total"'),
                    "legendFormat": "router_handler_total",
                },
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage="router_total"'),
                    "legendFormat": "router_total",
                },
                {
                    "expr": _expr("dtm.api.outer.duration_ms", env_name, 'operation="/api/v2/frontend",stage="http_shell_post_router"'),
                    "legendFormat": "http_shell_post_router",
                },
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",route="api",stage="handler_total"'),
                    "legendFormat": "handler_total",
                },
            ],
        ),
        (
            12,
            "Frontend Route Compare",
            [
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",stage="response_build",route="api"'),
                    "legendFormat": "api response_build",
                },
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",stage="response_build",route="bff"'),
                    "legendFormat": "bff response_build",
                },
                {
                    "expr": _expr("dtm.api.duration_ms", env_name, 'operation=~".*/api/v2/frontend"'),
                    "legendFormat": "{{operation}} total",
                },
            ],
        ),
        (
            13,
            "Frontend Cache Compare",
            [
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",cache_result="hit",stage=~".+"'),
                    "legendFormat": "hit {{route}} {{stage}}",
                },
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",cache_result="miss",stage=~".+"'),
                    "legendFormat": "miss {{route}} {{stage}}",
                },
                {
                    "expr": _expr("dtm.api.stage.duration_ms", env_name, 'operation="frontend_access",cache_result="bypass",stage=~".+"'),
                    "legendFormat": "bypass {{route}} {{stage}}",
                },
            ],
        ),
        (
            14,
            "Worker Reliability",
            [
                {"expr": _expr("dtm.worker.commands_total", env_name), "legendFormat": "commands_total"},
                {"expr": _expr("dtm.worker.command_failures_total", env_name), "legendFormat": "command_failures_total"},
                {"expr": _expr("dtm.worker.command_retries_total", env_name), "legendFormat": "command_retries_total"},
            ],
        ),
        (
            15,
            "Worker Timing",
            [
                {"expr": _expr("dtm.worker.command_duration_ms", env_name), "legendFormat": "command_duration_ms"},
                {"expr": _expr("dtm.worker.wall_clock_ms", env_name), "legendFormat": "wall_clock_ms"},
            ],
        ),
        (
            16,
            "Notify Runtime",
            [
                {"expr": _expr("dtm.notify.total", env_name), "legendFormat": "{{operation}} total"},
                {"expr": _expr("dtm.notify.duration_ms", env_name), "legendFormat": "{{operation}} duration_ms"},
                {"expr": _expr("dtm.notify.messages_sent", env_name), "legendFormat": "{{operation}} messages_sent"},
                {"expr": _expr("dtm.notify.tasks_selected", env_name), "legendFormat": "{{operation}} tasks_selected"},
            ],
        ),
        (
            17,
            "Telegram Intake",
            [
                {"expr": _expr("dtm.telegram.updates_total", env_name), "legendFormat": "updates_total"},
                {"expr": _expr("dtm.telegram.accepted_total", env_name), "legendFormat": "accepted_total"},
                {"expr": _expr("dtm.telegram.rejected_total", env_name), "legendFormat": "rejected_total"},
                {"expr": _expr("dtm.telegram.enqueue_ms", env_name), "legendFormat": "enqueue_ms"},
                {"expr": _expr("dtm.telegram.command_total", env_name), "legendFormat": "command_total"},
            ],
        ),
        (
            18,
            "Metrics Flush Duration",
            [
                {"expr": _expr("dtm.metrics.flush_duration_ms", env_name, 'backend=~".+"'), "legendFormat": "{{module}} {{operation}} {{backend}} {{result}}"},
            ],
        ),
        (
            19,
            "Metrics Flush Volume",
            [
                {"expr": _expr("dtm.metrics.flush_points_total", env_name, 'backend=~".+"'), "legendFormat": "{{module}} {{operation}} {{backend}} points"},
                {"expr": _expr("dtm.metrics.flush_failures_total", env_name, 'backend=~".+"'), "legendFormat": "{{module}} {{operation}} {{backend}} failures"},
            ],
        ),
    ]
    for index, (panel_id, title, targets) in enumerate(timeseries_specs):
        x = (index % 4) * 6
        y = timeseries_y + (index // 4) * 8
        panels.append(
            _timeseries_panel(
                panel_id=panel_id,
                title=title,
                targets=targets,
                datasource=datasource,
                x=x,
                y=y,
                w=6,
                h=8,
            )
        )
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

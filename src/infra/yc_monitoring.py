from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests


@dataclass(frozen=True, slots=True)
class MetricPoint:
    name: str
    value: float
    labels: dict[str, str]
    ts: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "labels": dict(self.labels),
            "value": self.value,
        }
        if self.ts:
            payload["ts"] = self.ts
        return payload


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_metric_labels(labels: dict[str, str] | None) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in dict(labels or {}).items():
        cleaned_key = str(key or "").strip()
        cleaned_value = str(value or "").strip()
        if not cleaned_key or not cleaned_value:
            continue
        normalized[cleaned_key] = cleaned_value
    return normalized


def build_metric_point(
    *,
    name: str,
    value: float,
    labels: dict[str, str] | None = None,
    service_label: str,
    namespace: str,
    ts: str | None = None,
) -> MetricPoint:
    merged_labels = normalize_metric_labels(labels)
    merged_labels.setdefault("service_name", str(service_label).strip())
    merged_labels.setdefault("namespace", str(namespace).strip())
    return MetricPoint(
        name=str(name).strip(),
        value=float(value),
        labels=merged_labels,
        ts=str(ts or "").strip() or _iso_now(),
    )


def write_metrics(
    *,
    endpoint_write: str,
    folder_id: str,
    iam_token: str,
    metrics: list[MetricPoint],
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    response = requests.post(
        str(endpoint_write).strip(),
        params={"folderId": str(folder_id).strip(), "service": "custom"},
        headers={
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
        },
        json={"metrics": [item.to_payload() for item in metrics]},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return dict(response.json() or {})


def _load_dashboard_grpc_modules() -> tuple[Any, Any, Any, Any]:
    import grpc
    from yandex.cloud.monitoring.v3 import chart_widget_pb2
    from yandex.cloud.monitoring.v3 import dashboard_pb2
    from yandex.cloud.monitoring.v3 import dashboard_service_pb2
    from yandex.cloud.monitoring.v3 import dashboard_service_pb2_grpc
    from yandex.cloud.monitoring.v3 import widget_pb2

    return grpc, chart_widget_pb2, dashboard_pb2, dashboard_service_pb2, dashboard_service_pb2_grpc, widget_pb2


def build_dashboard_widgets(*, env_name: str, namespace: str = "dtm") -> list[Any]:
    grpc, chart_widget_pb2, _dashboard_pb2, _dashboard_service_pb2, _dashboard_service_pb2_grpc, widget_pb2 = (
        _load_dashboard_grpc_modules()
    )
    del grpc, _dashboard_pb2, _dashboard_service_pb2, _dashboard_service_pb2_grpc

    def _chart(title: str, metric_name: str, x: int, y: int) -> Any:
        query = f'{metric_name}{{env="{env_name}",service="custom",namespace="{namespace}"}}'
        target_name = str(metric_name).replace(".", "_")
        return widget_pb2.Widget(
            position=widget_pb2.Widget.LayoutPosition(x=x, y=y, w=12, h=6),
            chart=chart_widget_pb2.ChartWidget(
                id=target_name,
                title=title,
                queries=chart_widget_pb2.ChartWidget.Queries(
                    targets=[chart_widget_pb2.ChartWidget.Queries.Target(query=query, name=target_name)]
                ),
            ),
        )

    return [
        _chart("Snapshot Updates", "dtm.snapshot.update_total", 0, 0),
        _chart("API Requests", "dtm.api.requests_total", 12, 0),
        _chart("Timeline Render", "dtm.render.total", 0, 6),
        _chart("Notify Runs", "dtm.notify.total", 12, 6),
        _chart("Telegram Updates", "dtm.telegram.accepted_total", 0, 12),
        _chart("Worker Commands", "dtm.worker.commands_total", 12, 12),
    ]


def list_dashboards(*, iam_token: str, folder_id: str, page_size: int = 100, endpoint: str = "monitoring.api.cloud.yandex.net:443") -> dict[str, Any]:
    grpc, _chart_widget_pb2, _dashboard_pb2, dashboard_service_pb2, dashboard_service_pb2_grpc, _widget_pb2 = (
        _load_dashboard_grpc_modules()
    )
    channel = grpc.secure_channel(str(endpoint).strip(), grpc.ssl_channel_credentials())
    stub = dashboard_service_pb2_grpc.DashboardServiceStub(channel)
    response = stub.List(
        dashboard_service_pb2.ListDashboardsRequest(folder_id=str(folder_id).strip(), page_size=int(page_size)),
        metadata=[("authorization", f"Bearer {iam_token}")],
        timeout=10,
    )
    items = [
        {
            "id": item.id,
            "name": item.name,
            "title": item.title,
            "etag": item.etag,
            "widgets": len(item.widgets),
        }
        for item in response.dashboards
    ]
    return {"dashboards": items, "next_page_token": str(response.next_page_token or "")}


def create_or_get_dashboard(
    *,
    iam_token: str,
    folder_id: str,
    name: str,
    title: str,
    description: str,
    widgets: list[Any],
    endpoint: str = "monitoring.api.cloud.yandex.net:443",
) -> dict[str, Any]:
    existing = list_dashboards(iam_token=iam_token, folder_id=folder_id, endpoint=endpoint)
    for item in existing.get("dashboards", []):
        if str(item.get("name")) == str(name):
            return {"status": "existing", **item}

    grpc, _chart_widget_pb2, dashboard_pb2, dashboard_service_pb2, dashboard_service_pb2_grpc, _widget_pb2 = (
        _load_dashboard_grpc_modules()
    )
    channel = grpc.secure_channel(str(endpoint).strip(), grpc.ssl_channel_credentials())
    stub = dashboard_service_pb2_grpc.DashboardServiceStub(channel)
    operation = stub.Create(
        dashboard_service_pb2.CreateDashboardRequest(
            folder_id=str(folder_id).strip(),
            name=str(name).strip(),
            title=str(title).strip(),
            description=str(description).strip(),
            widgets=list(widgets),
        ),
        metadata=[("authorization", f"Bearer {iam_token}")],
        timeout=20,
    )
    if not operation.done:
        return {"status": "pending", "operation_id": operation.id}
    if operation.error.code:
        return {
            "status": "error",
            "operation_id": operation.id,
            "error_code": operation.error.code,
            "error_message": operation.error.message,
        }
    dashboard = dashboard_pb2.Dashboard()
    operation.response.Unpack(dashboard)
    return {
        "status": "created",
        "operation_id": operation.id,
        "id": dashboard.id,
        "name": dashboard.name,
        "title": dashboard.title,
        "etag": dashboard.etag,
        "widgets": len(dashboard.widgets),
    }


def update_dashboard(
    *,
    iam_token: str,
    dashboard_id: str,
    etag: str,
    name: str,
    title: str,
    description: str,
    widgets: list[Any],
    endpoint: str = "monitoring.api.cloud.yandex.net:443",
) -> dict[str, Any]:
    grpc, _chart_widget_pb2, dashboard_pb2, dashboard_service_pb2, dashboard_service_pb2_grpc, _widget_pb2 = (
        _load_dashboard_grpc_modules()
    )
    channel = grpc.secure_channel(str(endpoint).strip(), grpc.ssl_channel_credentials())
    stub = dashboard_service_pb2_grpc.DashboardServiceStub(channel)
    operation = stub.Update(
        dashboard_service_pb2.UpdateDashboardRequest(
            dashboard_id=str(dashboard_id).strip(),
            etag=str(etag or "").strip(),
            name=str(name).strip(),
            title=str(title).strip(),
            description=str(description).strip(),
            widgets=list(widgets),
        ),
        metadata=[("authorization", f"Bearer {iam_token}")],
        timeout=20,
    )
    if not operation.done:
        return {"status": "pending", "operation_id": operation.id}
    if operation.error.code:
        return {
            "status": "error",
            "operation_id": operation.id,
            "error_code": operation.error.code,
            "error_message": operation.error.message,
        }
    dashboard = dashboard_pb2.Dashboard()
    operation.response.Unpack(dashboard)
    return {
        "status": "updated",
        "operation_id": operation.id,
        "id": dashboard.id,
        "name": dashboard.name,
        "title": dashboard.title,
        "etag": dashboard.etag,
        "widgets": len(dashboard.widgets),
    }

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from src.platform.integrations.datalens.specs import DataLensChartSpec, DataLensDashboardSpec


DATALENS_API_BASE = "https://api.datalens.tech"


def get_datalens_headers(iam_token: str, org_id: str) -> dict[str, str]:
    return {
        "x-yacloud-subjecttoken": str(iam_token or "").strip(),
        "x-dl-org-id": str(org_id or "").strip(),
        "x-dl-api-version": "1",
        "Content-Type": "application/json",
    }


def _request(*, method: str, path: str, iam_token: str, org_id: str, payload: dict[str, Any] | None = None, timeout_seconds: float = 15.0) -> dict[str, Any]:
    response = requests.request(
        method=method.upper(),
        url=f"{DATALENS_API_BASE}{path}",
        headers=get_datalens_headers(iam_token, org_id),
        json=payload if payload is not None else None,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return dict(response.json() or {})


def list_workbooks(*, iam_token: str, org_id: str) -> list[dict[str, Any]]:
    payload = _request(method="POST", path="/rpc/getWorkbooksList", iam_token=iam_token, org_id=org_id, payload={})
    return [dict(item) for item in list(payload.get("workbooks", []) or [])]


def find_workbook_by_name(*, iam_token: str, org_id: str, title: str) -> dict[str, Any] | None:
    title_value = str(title or "").strip()
    for item in list_workbooks(iam_token=iam_token, org_id=org_id):
        if str(item.get("title", "")).strip() == title_value:
            return item
    return None


def create_workbook(*, iam_token: str, org_id: str, title: str, description: str = "") -> dict[str, Any]:
    return _request(
        method="POST",
        path="/rpc/createWorkbook",
        iam_token=iam_token,
        org_id=org_id,
        payload={"title": str(title).strip(), "description": str(description or "").strip()},
    )


def find_or_create_workbook(*, iam_token: str, org_id: str, title: str, description: str = "") -> dict[str, Any]:
    existing = find_workbook_by_name(iam_token=iam_token, org_id=org_id, title=title)
    if existing is not None:
        return {"status": "existing", **existing}
    created = create_workbook(iam_token=iam_token, org_id=org_id, title=title, description=description)
    return {"status": "created", **created}


def find_connection_by_name(*, iam_token: str, org_id: str, workbook_id: str, name: str) -> dict[str, Any] | None:
    payload = _request(
        method="POST",
        path="/rpc/getWorkbook",
        iam_token=iam_token,
        org_id=org_id,
        payload={"workbookId": str(workbook_id).strip()},
    )
    entries = list(payload.get("entries", []) or [])
    for item in entries:
        if str(item.get("scope", "")).strip() != "connection":
            continue
        if str(item.get("name", "")).strip() == str(name).strip():
            return dict(item)
    return None


def create_monitoring_connection(
    *,
    iam_token: str,
    org_id: str,
    workbook_id: str,
    name: str,
    cloud_id: str,
    folder_id: str,
    service_account_id: str,
    description: str = "",
) -> dict[str, Any]:
    payload = {
        "type": "monitoring",
        "name": str(name).strip(),
        "description": str(description or "").strip(),
        "workbookId": str(workbook_id).strip(),
        "cloud_id": str(cloud_id).strip(),
        "folder_id": str(folder_id).strip(),
        "service_account_id": str(service_account_id).strip(),
        "dir_path": "/",
    }
    return _request(
        method="POST",
        path="/rpc/createConnection",
        iam_token=iam_token,
        org_id=org_id,
        payload=payload,
    )


def find_or_create_monitoring_connection(
    *,
    iam_token: str,
    org_id: str,
    workbook_id: str,
    name: str,
    cloud_id: str,
    folder_id: str,
    service_account_id: str,
    description: str = "",
) -> dict[str, Any]:
    existing = None
    if str(workbook_id).strip():
        existing = find_connection_by_name(
            iam_token=iam_token,
            org_id=org_id,
            workbook_id=workbook_id,
            name=name,
        )
    if existing is not None:
        return {"status": "existing", **existing}
    created = create_monitoring_connection(
        iam_token=iam_token,
        org_id=org_id,
        workbook_id=workbook_id,
        name=name,
        cloud_id=cloud_id,
        folder_id=folder_id,
        service_account_id=service_account_id,
        description=description,
    )
    return {"status": "created", **created}


@dataclass(frozen=True, slots=True)
class CreateChartResult:
    raw: dict[str, Any]

    @property
    def entry_id(self) -> str:
        return str(self.raw.get("entryId") or self.raw.get("id") or "").strip()


def create_ql_chart(
    *,
    iam_token: str,
    org_id: str,
    workbook_id: str,
    connection_entry_id: str,
    spec: DataLensChartSpec,
) -> CreateChartResult:
    payload = {
        "template": "ql",
        "workbookId": str(workbook_id).strip(),
        "name": str(spec.name).strip(),
        "annotation": {"description": str(spec.description).strip()},
        "data": {
            "connection": {"entryId": str(connection_entry_id).strip()},
            "queryType": "generic_query",
            "query": str(spec.query).strip(),
        },
    }
    result = _request(
        method="POST",
        path="/rpc/createQLChart",
        iam_token=iam_token,
        org_id=org_id,
        payload=payload,
        timeout_seconds=20.0,
    )
    return CreateChartResult(raw=result)


def _dashboard_item_for_chart(spec: DataLensChartSpec, chart_id: str) -> dict[str, Any]:
    return {
        "id": f"widget-{spec.key}",
        "namespace": "default",
        "type": "widget",
        "placement": {
            "x": spec.x,
            "y": spec.y,
            "w": spec.w,
            "h": spec.h,
        },
        "data": {
            "hideTitle": False,
            "tabs": [
                {
                    "id": f"tab-{spec.key}",
                    "title": spec.title,
                    "description": spec.description,
                    "chartId": str(chart_id).strip(),
                    "isDefault": True,
                    "params": {},
                }
            ],
        },
    }


def build_dashboard_entry(*, spec: DataLensDashboardSpec, chart_ids_by_key: dict[str, str]) -> dict[str, Any]:
    items: list[dict[str, Any]] = [
        {
            "id": "title-main",
            "namespace": "default",
            "type": "title",
            "placement": {"x": 0, "y": 0, "w": 24, "h": 1},
            "data": {"text": spec.title, "size": "l", "showInTOC": True},
        }
    ]
    for chart_spec in spec.charts:
        chart_id = str(chart_ids_by_key.get(chart_spec.key, "")).strip()
        if not chart_id:
            continue
        items.append(_dashboard_item_for_chart(chart_spec, chart_id))
    return {
        "name": spec.name,
        "entry": {
            "name": spec.name,
            "scope": "dashboard",
            "type": "dashboard",
            "data": {
                "counter": 1,
                "salt": spec.name.lower().replace(" ", "-"),
                "tabs": [
                    {
                        "id": "tab-main",
                        "title": spec.title,
                        "items": items,
                    }
                ],
            },
        },
    }


def create_dashboard(
    *,
    iam_token: str,
    org_id: str,
    spec: DataLensDashboardSpec,
    chart_ids_by_key: dict[str, str],
) -> dict[str, Any]:
    return _request(
        method="POST",
        path="/rpc/createDashboard",
        iam_token=iam_token,
        org_id=org_id,
        payload=build_dashboard_entry(spec=spec, chart_ids_by_key=chart_ids_by_key),
        timeout_seconds=20.0,
    )


def datalens_dashboard_url(org_id: str, dashboard_id: str) -> str:
    if not str(org_id or "").strip() or not str(dashboard_id or "").strip():
        return ""
    return f"https://datalens.yandex/{str(org_id).strip()}/{str(dashboard_id).strip()}"

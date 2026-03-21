from __future__ import annotations

from typing import Any

import requests


def grafana_headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {str(api_token or '').strip()}",
        "Content-Type": "application/json",
    }


def grafana_dashboard_url(public_base_url: str, dashboard_uid: str) -> str:
    return f"{str(public_base_url).rstrip('/')}/d/{str(dashboard_uid).strip()}"


def grafana_embed_url(public_base_url: str, dashboard_uid: str) -> str:
    return f"{grafana_dashboard_url(public_base_url, dashboard_uid)}?kiosk&theme=light"


def upsert_prometheus_datasource(
    *,
    base_url: str,
    api_token: str,
    name: str,
    datasource_url: str,
    bearer_token: str,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    base_url_value = str(base_url).rstrip("/")
    name_value = str(name or "").strip()
    headers = grafana_headers(api_token)
    response = requests.get(
        f"{base_url_value}/api/datasources/name/{name_value}",
        headers=headers,
        timeout=timeout_seconds,
    )
    if response.status_code == 200:
        existing = dict(response.json() or {})
        datasource_id = existing.get("id")
        if datasource_id is None:
            raise RuntimeError("grafana_datasource_missing_id")
        update_response = requests.put(
            f"{base_url_value}/api/datasources/{datasource_id}",
            headers=headers,
            json={
                "id": datasource_id,
                "uid": existing.get("uid"),
                "name": name_value,
                "type": "prometheus",
                "access": "proxy",
                "url": str(datasource_url).strip(),
                "basicAuth": False,
                "jsonData": {"httpHeaderName1": "Authorization"},
                "secureJsonData": {"httpHeaderValue1": f"Bearer {str(bearer_token).strip()}"},
            },
            timeout=timeout_seconds,
        )
        update_response.raise_for_status()
        return dict(update_response.json() or {})
    if response.status_code not in (404,):
        response.raise_for_status()
    create_response = requests.post(
        f"{base_url_value}/api/datasources",
        headers=headers,
        json={
            "name": name_value,
            "type": "prometheus",
            "access": "proxy",
            "url": str(datasource_url).strip(),
            "basicAuth": False,
            "jsonData": {"httpHeaderName1": "Authorization"},
            "secureJsonData": {"httpHeaderValue1": f"Bearer {str(bearer_token).strip()}"},
        },
        timeout=timeout_seconds,
    )
    create_response.raise_for_status()
    return dict(create_response.json() or {})


def get_datasource_by_name(
    *,
    base_url: str,
    api_token: str,
    name: str,
    timeout_seconds: float = 15.0,
) -> dict[str, Any] | None:
    response = requests.get(
        f"{str(base_url).rstrip('/')}/api/datasources/name/{str(name or '').strip()}",
        headers=grafana_headers(api_token),
        timeout=timeout_seconds,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return dict(response.json() or {})


def upsert_dashboard(
    *,
    base_url: str,
    api_token: str,
    dashboard: dict[str, Any],
    folder_uid: str | None = None,
    overwrite: bool = True,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"dashboard": dict(dashboard), "overwrite": bool(overwrite)}
    if str(folder_uid or "").strip():
        payload["folderUid"] = str(folder_uid).strip()
    response = requests.post(
        f"{str(base_url).rstrip('/')}/api/dashboards/db",
        headers=grafana_headers(api_token),
        json=payload,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return dict(response.json() or {})


def ensure_folder(
    *,
    base_url: str,
    api_token: str,
    title: str,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    title_value = str(title or "").strip()
    response = requests.get(
        f"{str(base_url).rstrip('/')}/api/folders",
        headers=grafana_headers(api_token),
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    for item in list(response.json() or []):
        if str(item.get("title", "")).strip() == title_value:
            return dict(item)
    create_response = requests.post(
        f"{str(base_url).rstrip('/')}/api/folders",
        headers=grafana_headers(api_token),
        json={"title": title_value},
        timeout=timeout_seconds,
    )
    create_response.raise_for_status()
    return dict(create_response.json() or {})

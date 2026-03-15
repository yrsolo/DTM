from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import requests

from src.infra.yc_iam import auth_headers, get_iam_token


FUNCTIONS_API_BASE = "https://serverless-functions.api.cloud.yandex.net/functions/v1"


@dataclass(frozen=True, slots=True)
class FunctionBuildInfo:
    function_name: str
    active_version_id: str
    deployed_at: str
    runtime: str
    memory: str
    timeout_seconds: int
    entrypoint: str
    service_account_id: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

def _iso_to_z(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text.endswith("+00:00"):
        return text.replace("+00:00", "Z")
    return text


def get_function_build_info(
    *,
    folder_id: str,
    function_name: str,
    sa_json_credentials: str | None,
    sa_key_file: str | None,
    timeout_seconds: float = 4.0,
) -> FunctionBuildInfo:
    iam_token = get_iam_token(sa_json_credentials, sa_key_file, timeout_seconds=timeout_seconds)
    list_response = requests.get(
        f"{FUNCTIONS_API_BASE}/functions",
        params={"folderId": str(folder_id).strip()},
        headers=auth_headers(iam_token),
        timeout=timeout_seconds,
    )
    list_response.raise_for_status()
    items = list(list_response.json().get("functions", []) or [])
    function_item = next(
        (item for item in items if str(item.get("name", "")).strip() == str(function_name).strip()),
        None,
    )
    if function_item is None:
        raise RuntimeError(f"Function not found: {function_name}")
    function_id = str(function_item.get("id", "")).strip()
    version_response = requests.get(
        f"{FUNCTIONS_API_BASE}/versions:byTag",
        params={"functionId": function_id, "tag": "$latest"},
        headers=auth_headers(iam_token),
        timeout=timeout_seconds,
    )
    version_response.raise_for_status()
    version_item = dict(version_response.json() or {})
    resources = dict(version_item.get("resources", {}) or {})
    execution_timeout = str(version_item.get("executionTimeout", "")).strip()
    timeout_seconds_value = 0
    if execution_timeout.endswith("s"):
        try:
            timeout_seconds_value = int(float(execution_timeout[:-1]))
        except ValueError:
            timeout_seconds_value = 0
    return FunctionBuildInfo(
        function_name=str(function_item.get("name", "")).strip() or str(function_name).strip(),
        active_version_id=str(version_item.get("id", "")).strip(),
        deployed_at=_iso_to_z(str(version_item.get("createdAt", "")).strip()),
        runtime=str(version_item.get("runtime", "")).strip(),
        memory=str(resources.get("memory", "")).strip(),
        timeout_seconds=timeout_seconds_value,
        entrypoint=str(version_item.get("entrypoint", "")).strip(),
        service_account_id=str(version_item.get("serviceAccountId", "")).strip(),
    )

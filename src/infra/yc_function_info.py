from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
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


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _load_sa_key(raw_json: str | None, file_path: str | None) -> dict[str, Any]:
    raw = str(raw_json or "").strip()
    if raw:
        try:
            return dict(json.loads(raw))
        except Exception:
            decoded = base64.b64decode(raw).decode("utf-8")
            return dict(json.loads(decoded))
    path = Path(str(file_path or "").strip())
    if path.exists():
        return dict(json.loads(path.read_text(encoding="utf-8")))
    raise RuntimeError("Yandex service account key is unavailable.")


def _create_iam_jwt(key_data: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    header = {"alg": "PS256", "typ": "JWT", "kid": str(key_data.get("id", "")).strip()}
    payload = {
        "aud": IAM_TOKEN_URL,
        "iss": str(key_data.get("service_account_id", "")).strip(),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    signing_input = f"{_b64url(json.dumps(header, separators=(',', ':')).encode('utf-8'))}.{_b64url(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}".encode("ascii")
    private_key = serialization.load_pem_private_key(
        str(key_data.get("private_key", "")).encode("utf-8"),
        password=None,
    )
    signature = private_key.sign(
        signing_input,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return f"{signing_input.decode('ascii')}.{_b64url(signature)}"


def _iam_token_from_sa(raw_json: str | None, file_path: str | None, timeout_seconds: float = 4.0) -> str:
    key_data = _load_sa_key(raw_json, file_path)
    response = requests.post(
        IAM_TOKEN_URL,
        json={"jwt": _create_iam_jwt(key_data)},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("iamToken", "")).strip()


def _auth_headers(iam_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {iam_token}"}


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
    iam_token = _iam_token_from_sa(sa_json_credentials, sa_key_file, timeout_seconds=timeout_seconds)
    list_response = requests.get(
        f"{FUNCTIONS_API_BASE}/functions",
        params={"folderId": str(folder_id).strip()},
        headers=_auth_headers(iam_token),
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
        f"{FUNCTIONS_API_BASE}/functions/{function_id}:getVersionByTag",
        params={"tag": "$latest"},
        headers=_auth_headers(iam_token),
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

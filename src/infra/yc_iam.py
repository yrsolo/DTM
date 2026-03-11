from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
METADATA_TOKEN_URL = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def load_service_account_key(raw_json: str | None, file_path: str | None) -> dict[str, Any]:
    raw = str(raw_json or "").strip()
    if raw:
        try:
            return dict(json.loads(raw))
        except Exception:
            decoded = base64.b64decode(raw).decode("utf-8")
            return dict(json.loads(decoded))
    path_value = str(file_path or "").strip()
    if not path_value:
        raise RuntimeError("Yandex service account key is unavailable.")
    path = Path(path_value)
    if path.exists() and path.is_file():
        return dict(json.loads(path.read_text(encoding="utf-8")))
    raise RuntimeError("Yandex service account key is unavailable.")


def create_iam_jwt(key_data: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    header = {"alg": "PS256", "typ": "JWT", "kid": str(key_data.get("id", "")).strip()}
    payload = {
        "aud": IAM_TOKEN_URL,
        "iss": str(key_data.get("service_account_id", "")).strip(),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    signing_input = (
        f"{_b64url(json.dumps(header, separators=(',', ':')).encode('utf-8'))}."
        f"{_b64url(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}"
    ).encode("ascii")
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


def get_metadata_token(timeout_seconds: float = 2.0) -> str:
    response = requests.get(
        METADATA_TOKEN_URL,
        headers={"Metadata-Flavor": "Google"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("access_token") or payload.get("iamToken") or "").strip()


def get_iam_token(raw_json: str | None, file_path: str | None, timeout_seconds: float = 4.0) -> str:
    if str(raw_json or "").strip() or str(file_path or "").strip():
        key_data = load_service_account_key(raw_json, file_path)
        response = requests.post(
            IAM_TOKEN_URL,
            json={"jwt": create_iam_jwt(key_data)},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        token = str(payload.get("iamToken", "")).strip()
        if not token:
            raise RuntimeError("IAM token response does not contain iamToken.")
        return token
    token = get_metadata_token(timeout_seconds=timeout_seconds)
    if not token:
        raise RuntimeError("Metadata token response does not contain access_token.")
    return token


def auth_headers(iam_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {iam_token}"}

"""Cloud smoke: trigger sync/build and verify frontend v2 snapshot endpoint."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlencode

import requests


def _http_get(url: str, *, params: dict[str, str] | None = None, timeout: int = 60) -> requests.Response:
    response = requests.get(url, params=params, timeout=timeout)
    return response


def main() -> int:
    parser = argparse.ArgumentParser(description="DB migration v2 cloud smoke")
    parser.add_argument("--base-url", required=True, help="Function base URL, example https://...yandexcloud.net/<id>")
    parser.add_argument("--api-url", default="", help="Optional explicit API v2 URL (if differs from base-url/api/v2/frontend)")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    sync_params = {"mode": "sync-only", "force_refresh": "1"}
    sync_response = _http_get(base_url, params=sync_params, timeout=args.timeout)
    print(f"sync_status_code={sync_response.status_code}")
    print(f"sync_request_query={urlencode(sync_params)}")
    print(f"sync_body={sync_response.text[:500]}")
    if sync_response.status_code != 200:
        print("api_ok=false")
        return 1

    api_url = args.api_url.strip() or f"{base_url}/api/v2/frontend"
    api_response = _http_get(api_url, timeout=args.timeout)
    print(f"api_status_code={api_response.status_code}")
    if api_response.status_code != 200:
        print("api_ok=false")
        return 1
    try:
        payload = api_response.json()
    except json.JSONDecodeError:
        print("api_ok=false")
        print("api_error=invalid_json")
        return 1

    tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
    meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
    if not isinstance(tasks, list):
        print("api_ok=false")
        print("api_error=tasks_not_list")
        return 1
    if not isinstance(meta, dict) or not meta.get("contractVersion"):
        print("api_ok=false")
        print("api_error=meta_contract_missing")
        return 1

    print(f"api_contract_version={meta.get('contractVersion')}")
    print(f"api_tasks_count={len(tasks)}")
    print("api_ok=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

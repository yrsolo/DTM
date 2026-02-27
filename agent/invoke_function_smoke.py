"""Simple smoke invoke utility for Yandex Cloud Function HTTP endpoint."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests


def load_env(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    parser = argparse.ArgumentParser(description="Invoke cloud function endpoint for smoke check")
    parser.add_argument("--url", default="", help="Function URL (defaults to YC_FUNCTION_URL env)")
    parser.add_argument(
        "--event-file",
        default="",
        help="Optional path to JSON file used as request body",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    args = parser.parse_args()

    load_env()
    url = args.url or os.environ.get("YC_FUNCTION_URL", "").strip()
    if not url:
        print("ERROR: function URL is required (pass --url or set YC_FUNCTION_URL)")
        return 2

    payload = {}
    if args.event_file:
        payload = json.loads(Path(args.event_file).read_text(encoding="utf-8"))

    response = requests.post(url, json=payload, timeout=args.timeout)
    print(f"status_code={response.status_code}")
    print(response.text)
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

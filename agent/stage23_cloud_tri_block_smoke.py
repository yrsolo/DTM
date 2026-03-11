"""Stage 23 cloud tri-block smoke: sync invoke + API v1/v2 parity evidence."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _http_get(url: str, *, params: dict[str, str] | None = None, timeout: int = 60) -> requests.Response:
    return requests.get(url, params=params, timeout=timeout)


def _extract_v1_task_ids(payload: dict[str, object]) -> list[str]:
    tasks = payload.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    result: list[str] = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("id", "")).strip()
        if task_id:
            result.append(task_id)
    return sorted(set(result))


def _extract_v2_task_ids(payload: dict[str, object]) -> list[str]:
    tasks = payload.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    result: list[str] = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("id", "")).strip()
        if task_id:
            result.append(task_id)
    return sorted(set(result))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage 23 cloud tri-block smoke")
    parser.add_argument("--function-url", default="", help="Cloud function URL (fallback: YC_FUNCTION_URL env)")
    parser.add_argument("--api-base", default="", help="API base URL (for example https://dtm.solofarm.ru/test)")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument(
        "--output-file",
        default="artifacts/tmp/stage23_cloud_tri_block_smoke.json",
        help="Path to save evidence JSON",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv(".env")
    args = _parse_args()
    function_url = (args.function_url or os.environ.get("YC_FUNCTION_URL", "")).strip()
    api_base = (args.api_base or os.environ.get("API_BASE_URL", "")).strip().rstrip("/")
    if not function_url:
        print("ERROR: missing function URL (--function-url or YC_FUNCTION_URL)")
        return 2
    if not api_base:
        print("ERROR: missing API base (--api-base or API_BASE_URL)")
        return 2

    evidence: dict[str, object] = {
        "artifact": "stage23_cloud_tri_block_smoke",
        "generated_at_utc": _utc_iso(),
        "function_url": function_url,
        "api_base": api_base,
    }

    sync_params = {"mode": "sync-only", "force_refresh": "1"}
    sync_response = _http_get(function_url, params=sync_params, timeout=args.timeout)
    evidence["sync_invoke"] = {
        "status_code": sync_response.status_code,
        "query": urlencode(sync_params),
        "body_prefix": sync_response.text[:300],
    }
    if sync_response.status_code != 200:
        evidence["ok"] = False
        Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_file).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"stage23_cloud_tri_block_smoke_file={args.output_file}")
        print("stage23_cloud_tri_block_smoke_ok=false")
        return 1

    v1_url = f"{api_base}/api/v1/frontend"
    v2_url = f"{api_base}/api/v2/frontend"
    v1_response = _http_get(v1_url, timeout=args.timeout)
    v2_response = _http_get(v2_url, timeout=args.timeout)

    if v1_response.status_code != 200 or v2_response.status_code != 200:
        evidence["ok"] = False
        evidence["api"] = {
            "v1_status_code": v1_response.status_code,
            "v2_status_code": v2_response.status_code,
        }
        Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_file).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"stage23_cloud_tri_block_smoke_file={args.output_file}")
        print("stage23_cloud_tri_block_smoke_ok=false")
        return 1

    try:
        v1_payload = v1_response.json()
        v2_payload = v2_response.json()
    except json.JSONDecodeError:
        evidence["ok"] = False
        evidence["api"] = {
            "v1_status_code": v1_response.status_code,
            "v2_status_code": v2_response.status_code,
            "json_decode_error": True,
        }
        Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_file).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"stage23_cloud_tri_block_smoke_file={args.output_file}")
        print("stage23_cloud_tri_block_smoke_ok=false")
        return 1

    v1_ids = _extract_v1_task_ids(v1_payload if isinstance(v1_payload, dict) else {})
    v2_ids = _extract_v2_task_ids(v2_payload if isinstance(v2_payload, dict) else {})
    ids_overlap = sorted(set(v1_ids).intersection(v2_ids))
    evidence["api"] = {
        "v1_status_code": v1_response.status_code,
        "v2_status_code": v2_response.status_code,
        "v1_tasks_count": len(v1_ids),
        "v2_tasks_count": len(v2_ids),
        "overlap_count": len(ids_overlap),
        "v2_contract_version": (
            str((v2_payload or {}).get("meta", {}).get("contractVersion", ""))
            if isinstance(v2_payload, dict)
            else ""
        ),
        "v2_readmodel_source": (
            str((v2_payload or {}).get("meta", {}).get("readmodelSource", ""))
            if isinstance(v2_payload, dict)
            else ""
        ),
        "sample_overlap_ids": ids_overlap[:10],
    }
    evidence["ok"] = len(ids_overlap) > 0

    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_file).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"stage23_cloud_tri_block_smoke_file={args.output_file}")
    print(f"stage23_cloud_tri_block_smoke_ok={str(bool(evidence['ok'])).lower()}")
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Cloud render freshness smoke: wait deploy, invoke function, validate sheet timestamp freshness."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import gettempdir
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

DEFAULT_WORKFLOW_FILE = "deploy_yc_function_main.yml"
DEFAULT_WORKSHEET_NAME = "Задачи"
DEFAULT_TIMESTAMP_CELL = "A1"
DEFAULT_TIMEZONE = "Europe/Moscow"

EN_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

RU_MONTHS = {
    "январь": 1,
    "января": 1,
    "февраль": 2,
    "февраля": 2,
    "март": 3,
    "марта": 3,
    "апрель": 4,
    "апреля": 4,
    "май": 5,
    "мая": 5,
    "июнь": 6,
    "июня": 6,
    "июль": 7,
    "июля": 7,
    "август": 8,
    "августа": 8,
    "сентябрь": 9,
    "сентября": 9,
    "октябрь": 10,
    "октября": 10,
    "ноябрь": 11,
    "ноября": 11,
    "декабрь": 12,
    "декабря": 12,
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _load_google_key_path() -> str:
    key_path = _env("GOOGLE_KEY_JSON_PATH")
    if key_path:
        return key_path

    key_b64 = _env("GOOGLE_KEY_JSON_B64")
    key_text = _env("GOOGLE_KEY_JSON")
    if key_b64:
        key_text = base64.b64decode(key_b64).decode("utf-8")

    if key_text:
        tmp_file = Path(gettempdir()) / "dtm_google_key_smoke.json"
        tmp_file.write_text(key_text, encoding="utf-8")
        return str(tmp_file)

    return "key/google_key_poised-backbone-191400-4e9fc454915f.json"


def _api_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    req = Request(url=url, headers=headers or {}, method="GET")
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def _post_json(url: str, payload: dict[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url=url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=60) as resp:
            status = resp.getcode()
            text = resp.read().decode("utf-8", errors="replace")
            return status, text
    except HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return exc.code, text
    except URLError as exc:
        return 0, str(exc)


def _wait_for_deploy(
    *,
    owner: str,
    repo: str,
    token: str,
    workflow_file: str,
    branch: str,
    timeout_sec: int,
    poll_sec: int,
) -> int:
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    runs_url = (
        f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/runs?"
        + urlencode({"per_page": 1, "branch": branch})
    )
    start = time.time()
    run_id = 0
    while True:
        payload = _api_json(runs_url, headers)
        runs = payload.get("workflow_runs", [])
        if not runs:
            raise RuntimeError("no_deploy_runs_found")
        run = runs[0]
        run_id = int(run.get("id", 0))
        status = str(run.get("status", ""))
        conclusion = str(run.get("conclusion", ""))
        print(f"deploy_wait run_id={run_id} status={status} conclusion={conclusion}")
        if status == "completed":
            if conclusion == "success":
                return run_id
            raise RuntimeError(f"deploy_failed run_id={run_id} conclusion={conclusion}")
        if time.time() - start > timeout_sec:
            raise TimeoutError(f"deploy_wait_timeout run_id={run_id} timeout_sec={timeout_sec}")
        time.sleep(poll_sec)


def _read_sheet_cell(
    *,
    credentials_path: str,
    spreadsheet_name: str,
    worksheet_name: str,
    cell: str,
) -> str:
    creds = Credentials.from_service_account_file(credentials_path)
    sheets = build("sheets", "v4", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    files = (
        drive.files()
        .list(q=f"name='{spreadsheet_name}'", fields="files(id,name)")
        .execute()
        .get("files", [])
    )
    if not files:
        raise RuntimeError(f"spreadsheet_not_found name={spreadsheet_name}")
    spreadsheet_id = files[0]["id"]

    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{worksheet_name}!{cell}")
        .execute()
    )
    values = result.get("values", [])
    if not values or not values[0]:
        return ""
    return str(values[0][0]).strip()


def _parse_corner_timestamp(value: str, now_local: datetime) -> datetime:
    # Expected producer format: "%H:%M %B %d".
    text = value.strip()
    match = re.match(r"^(\d{1,2}):(\d{2})\s+([^\s]+)\s+(\d{1,2})$", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"unsupported_timestamp_format value={value!r}")

    hour = int(match.group(1))
    minute = int(match.group(2))
    month_token = match.group(3).strip().lower()
    day = int(match.group(4))

    month = EN_MONTHS.get(month_token) or RU_MONTHS.get(month_token)
    if month is None:
        raise ValueError(f"unknown_month_token token={month_token!r} value={value!r}")

    parsed = now_local.replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)

    # If parsed appears far in future because of year boundary, move to previous year.
    if parsed - now_local > timedelta(days=2):
        parsed = parsed.replace(year=parsed.year - 1)
    return parsed


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cloud render freshness smoke")
    parser.add_argument("--url", default="", help="Function URL (or YC_FUNCTION_URL env)")
    parser.add_argument("--mode", default="timer", help="Invoke mode (default: timer)")
    parser.add_argument("--dry-run", action="store_true", help="Set dry_run=true in invoke payload")
    parser.add_argument("--mock-external", action="store_true", help="Set mock_external=true in invoke payload")

    parser.add_argument("--wait-deploy", action="store_true", help="Wait for latest deploy workflow success")
    parser.add_argument("--github-owner", default=_env("GITHUB_OWNER"), help="GitHub owner")
    parser.add_argument("--github-repo", default=_env("GITHUB_REPO"), help="GitHub repo")
    parser.add_argument("--github-token", default=_env("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--workflow-file", default=DEFAULT_WORKFLOW_FILE, help="Deploy workflow file")
    parser.add_argument("--workflow-branch", default="main", help="Deploy workflow branch")
    parser.add_argument("--deploy-timeout-sec", type=int, default=1200, help="Max wait for deploy")
    parser.add_argument("--deploy-poll-sec", type=int, default=15, help="Poll interval for deploy")

    parser.add_argument("--spreadsheet-name", default=_env("TARGET_SHEET_NAME"), help="Google spreadsheet name")
    parser.add_argument("--worksheet-name", default=DEFAULT_WORKSHEET_NAME, help="Worksheet title")
    parser.add_argument("--timestamp-cell", default=DEFAULT_TIMESTAMP_CELL, help="Cell with render timestamp")
    parser.add_argument("--google-key-json-path", default=_load_google_key_path(), help="Service-account json path")

    parser.add_argument(
        "--max-age-minutes",
        type=int,
        default=20,
        help="Maximum allowed age for corner timestamp",
    )
    parser.add_argument(
        "--post-invoke-wait-sec",
        type=int,
        default=10,
        help="Wait after invoke before reading timestamp",
    )
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE, help="Timezone for freshness check")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = _args()

    function_url = args.url or _env("YC_FUNCTION_URL")
    if not function_url:
        raise SystemExit("function_url_missing: pass --url or set YC_FUNCTION_URL")

    if args.wait_deploy:
        if not (args.github_owner and args.github_repo and args.github_token):
            raise SystemExit("github_credentials_missing for --wait-deploy")
        run_id = _wait_for_deploy(
            owner=args.github_owner,
            repo=args.github_repo,
            token=args.github_token,
            workflow_file=args.workflow_file,
            branch=args.workflow_branch,
            timeout_sec=args.deploy_timeout_sec,
            poll_sec=args.deploy_poll_sec,
        )
        print(f"deploy_ready run_id={run_id}")

    payload: dict[str, Any] = {"mode": args.mode}
    if args.dry_run:
        payload["dry_run"] = True
    if args.mock_external:
        payload["mock_external"] = True

    status, body = _post_json(function_url, payload)
    print(f"invoke_status={status}")
    print(f"invoke_body={body}")
    if status != 200:
        raise SystemExit("invoke_failed")

    if args.post_invoke_wait_sec > 0:
        time.sleep(args.post_invoke_wait_sec)

    from zoneinfo import ZoneInfo

    now_local = datetime.now(ZoneInfo(args.timezone))
    corner_value = _read_sheet_cell(
        credentials_path=args.google_key_json_path,
        spreadsheet_name=args.spreadsheet_name,
        worksheet_name=args.worksheet_name,
        cell=args.timestamp_cell,
    )
    print(f"corner_value={corner_value}")
    if not corner_value:
        raise SystemExit("timestamp_cell_empty")

    ts = _parse_corner_timestamp(corner_value, now_local)
    age_minutes = (now_local - ts).total_seconds() / 60.0
    print(f"corner_timestamp_iso={ts.isoformat()}")
    print(f"corner_age_minutes={age_minutes:.1f}")

    if age_minutes < -5:
        raise SystemExit("timestamp_in_future_too_far")
    if age_minutes > float(args.max_age_minutes):
        raise SystemExit(
            f"timestamp_too_old age_minutes={age_minutes:.1f} max_age_minutes={args.max_age_minutes}"
        )

    print("cloud_render_freshness_smoke_ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
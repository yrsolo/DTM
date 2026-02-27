"""Send owner decision request notifications to Telegram.

Usage:
    python agent/notify_owner.py --title "Decision needed" --details "Pick A or B"
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError

from dotenv import load_dotenv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Notify repository owner via Telegram")
    parser.add_argument("--title", required=True, help="Short title of required decision")
    parser.add_argument("--details", required=True, help="What decision is needed")
    parser.add_argument(
        "--options",
        default="",
        help="Optional short options, e.g. '1) keep legacy; 2) refactor now'",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Optional context: branch/task/file or other useful pointers",
    )
    return parser


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _send_message(token: str, chat_id: str, message: str) -> None:
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            if '"ok":true' not in body:
                raise RuntimeError("Telegram API returned non-ok response")
    except HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            details = str(exc)
        raise RuntimeError(f"HTTP {exc.code}: {details}") from exc


def main() -> int:
    load_dotenv()
    args = _build_parser().parse_args()

    try:
        token = _require_env("TG_AGENT_TOKEN")
        chat_id = _require_env("MY_CHAT_ID")
    except RuntimeError as exc:
        print(str(exc))
        return 2

    lines = [
        "DTM Agent requires owner decision",
        f"Title: {args.title}",
        f"Details: {args.details}",
    ]
    if args.options:
        lines.append(f"Options: {args.options}")
    if args.context:
        lines.append(f"Context: {args.context}")
    message = "\n".join(lines)

    try:
        _send_message(token=token, chat_id=chat_id, message=message)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to send Telegram notification: {exc}")
        return 1

    print("Owner notification sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

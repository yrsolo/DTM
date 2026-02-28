"""Send owner notifications to Telegram.

Usage:
    python agent/notify_owner.py --mode blocked --title "❓ Нужен выбор" --details "Опиши решение"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError

from dotenv import load_dotenv

CYRILLIC_PATTERN = re.compile(r"[А-Яа-яЁё]")
LATIN_PATTERN = re.compile(r"[A-Za-z]")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Notify repository owner via Telegram")
    parser.add_argument(
        "--mode",
        choices=("blocked", "info"),
        default="blocked",
        help="Notification mode: blocked=owner action required, info=for awareness only.",
    )
    parser.add_argument("--title", required=True, help="Short notification title")
    parser.add_argument("--details", required=True, help="Notification details")
    parser.add_argument(
        "--options",
        default="",
        help="Optional short options, e.g. '1) оставить как есть; 2) исправить сейчас'",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Optional context: branch/task/file or other useful pointers",
    )
    return parser


def _safe_print(text: str) -> None:
    """Print text safely on consoles with narrow encodings."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


def _validate_ru_field(name: str, value: str, required: bool = True) -> None:
    text = (value or "").strip()
    if required and not text:
        raise ValueError(f"Поле '{name}' не может быть пустым")
    if not text:
        return
    if LATIN_PATTERN.search(text):
        raise ValueError(f"Поле '{name}' должно содержать только русский текст (без латиницы)")
    if not CYRILLIC_PATTERN.search(text):
        raise ValueError(f"Поле '{name}' должно содержать русский текст")


def _validate_ru_payload(args: argparse.Namespace) -> None:
    _validate_ru_field("title", args.title, required=True)
    _validate_ru_field("details", args.details, required=True)
    _validate_ru_field("options", args.options, required=False)
    _validate_ru_field("context", args.context, required=False)


def _build_message(args: argparse.Namespace) -> str:
    if args.mode == "blocked":
        lead = "DTM агент: 🚨 требуется участие владельца (работа остановлена)"
    else:
        lead = "DTM агент: ✅ информационное обновление (участие не требуется)"

    lines = [
        lead,
        f"Заголовок: {args.title}",
        f"Детали: {args.details}",
    ]
    if args.options:
        lines.append(f"Варианты: {args.options}")
    if args.context:
        lines.append(f"Контекст: {args.context}")
    return "\n".join(lines)


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
        _validate_ru_payload(args)
    except ValueError as exc:
        _safe_print(f"Ошибка валидации payload: {exc}")
        return 2

    try:
        token = _require_env("TG_AGENT_TOKEN")
        chat_id = _require_env("MY_CHAT_ID")
    except RuntimeError as exc:
        _safe_print(str(exc))
        return 2

    message = _build_message(args)

    try:
        _send_message(token=token, chat_id=chat_id, message=message)
    except Exception as exc:  # noqa: BLE001
        _safe_print(f"Failed to send Telegram notification: {exc}")
        return 1

    _safe_print("Уведомление владельцу отправлено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
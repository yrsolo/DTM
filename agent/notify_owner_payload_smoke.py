"""Smoke checks for RU-only payload validation in notify_owner helper."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.notify_owner import _validate_ru_payload


class _Args:
    def __init__(self, title: str, details: str, options: str = "", context: str = "") -> None:
        self.title = title
        self.details = details
        self.options = options
        self.context = context


def run() -> None:
    _validate_ru_payload(
        _Args(
            title="❓ Нужен выбор",
            details="Требуется решение по инциденту и следующий шаг.",
            options="1) создать новый чат; 2) ответить тимлиду",
            context="задача дтм 50",
        )
    )

    latin_failed = False
    try:
        _validate_ru_payload(
            _Args(
                title="Decision required",
                details="Pick A or B",
            )
        )
    except ValueError:
        latin_failed = True

    assert latin_failed is True
    print("notify_owner_payload_smoke_ok")


if __name__ == "__main__":
    run()

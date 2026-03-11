from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def now_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(str(timezone_name or "UTC").strip() or "UTC"))


def today_in_timezone(timezone_name: str) -> date:
    return now_in_timezone(timezone_name).date()


def format_sheet_timestamp(value: datetime) -> str:
    target = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return target.strftime("%H:%M %B %d")

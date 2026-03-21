"""Canonical top-level runtime modes for the target entrypoint package."""

from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    HTTP_ACCESS_API = "http_access_api"
    TELEGRAM_WEBHOOK = "telegram_webhook"
    QUEUE_WORKER = "queue_worker"
    TRIGGER_TIMER = "trigger_timer"
    TRIGGER_MORNING = "trigger_morning"
    HEALTHCHECK = "healthcheck"
    UNKNOWN = "unknown"


from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class StructuredLogger:
    def info(self, event: str, **fields: Any) -> None:
        raise NotImplementedError

    def warning(self, event: str, **fields: Any) -> None:
        raise NotImplementedError

    def error(self, event: str, **fields: Any) -> None:
        raise NotImplementedError


class StdoutJsonLogger(StructuredLogger):
    def _serialize(self, event: str, *, level: str, **fields: Any) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "level": str(level).strip().lower(),
            "event": str(event).strip(),
        }
        for key, value in fields.items():
            if value is None:
                continue
            payload[str(key)] = value
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _emit(self, level: str, event: str, **fields: Any) -> None:
        print(self._serialize(event, level=level, **fields))

    def info(self, event: str, **fields: Any) -> None:
        self._emit("info", event, **fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._emit("warning", event, **fields)

    def error(self, event: str, **fields: Any) -> None:
        self._emit("error", event, **fields)

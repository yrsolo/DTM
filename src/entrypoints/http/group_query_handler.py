"""Group-query HTTP handler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd

from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.response_utils import json_response
from src.entrypoints_adapters.api_v2_adapter import build_frontend_query
from src.legacy.http_core_bindings import build_deadlines_reply, build_tasks_reply, parse_group_query_request
from src.snapshot_engine import build_snapshot_engine


@dataclass(slots=True)
class _GroupTaskProjection:
    name: str
    designer: str
    timing: dict[pd.Timestamp, list[str]]

    @property
    def max_date(self) -> pd.Timestamp | None:
        return max(self.timing.keys()) if self.timing else None


def _parse_iso_day(value: str) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return pd.Timestamp(datetime.fromisoformat(text[:10]))
    except Exception:
        return None


def _group_tasks_from_payload(payload: dict[str, Any]) -> list[_GroupTaskProjection]:
    people = payload.get("entities", {}).get("people", [])
    owner_map: dict[str, str] = {}
    for person in people if isinstance(people, list) else []:
        if not isinstance(person, dict):
            continue
        person_id = str(person.get("id", "")).strip()
        person_name = str(person.get("name", "")).strip()
        if person_id:
            owner_map[person_id] = person_name

    result: list[_GroupTaskProjection] = []
    tasks = payload.get("tasks", [])
    for task in tasks if isinstance(tasks, list) else []:
        if not isinstance(task, dict):
            continue
        designer = owner_map.get(str(task.get("ownerId", "")).strip(), "")
        timing: dict[pd.Timestamp, list[str]] = {}
        milestones = task.get("milestones", [])
        for milestone in milestones if isinstance(milestones, list) else []:
            if not isinstance(milestone, dict):
                continue
            when = _parse_iso_day(str(milestone.get("planned", "")))
            if when is None:
                continue
            stage = str(milestone.get("type", "")).strip()
            if not stage:
                continue
            timing.setdefault(when, []).append(stage)
        if not timing:
            fallback = _parse_iso_day(str(task.get("date", {}).get("end", "")))
            if fallback is not None:
                timing[fallback] = ["stage"]
        result.append(
            _GroupTaskProjection(
                name=str(task.get("title", "")).strip(),
                designer=designer,
                timing=timing,
            )
        )
    return result


class GroupQueryHandler:
    """Telegram group query webhook handler."""

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    async def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None

        deps = self._ctx.deps
        bot_username = str(deps.get("tg_bot_username", ""))
        query = parse_group_query_request(req.body, bot_username=bot_username)
        if query is None:
            return None

        notifier = TelegramNotifier(
            bot_token=str(deps.get("tg_bot_token", "")),
            default_chat_id=deps.get("default_chat_id"),
        )
        try:
            snapshot_engine = build_snapshot_engine(self._ctx)
            payload = snapshot_engine.frontend_v2(
                build_frontend_query(
                    statuses=["work", "pre_done"],
                    designer="",
                    limit=2000,
                    include_people=True,
                    window_data={"enabled": False, "start": None, "end": None, "mode": "intersects"},
                )
            )
            tasks = _group_tasks_from_payload(payload)
            if query.action == "deadlines":
                reply = build_deadlines_reply(tasks)
            else:
                reply = build_tasks_reply(tasks, requester_name=query.requester_name)
            await notifier.send_message(query.chat_id, reply, parse_mode=None)
            return json_response(200, {"artifact": "group_query", "status": "ok"})
        except Exception as error:
            print(f"group_query_error={error}")
            await notifier.send_message(
                query.chat_id,
                "?? ?????? ??????? ?????? ?????. ?????????? ??? ??? ????? ??????.",
                parse_mode=None,
            )
            return json_response(200, {"artifact": "group_query", "status": "error"})

"""Deterministic masking for browser-facing frontend payloads."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Any

from src.entrypoints.http.access_context import AccessContext


DESIGNER_DICTIONARY = (
    "Tom Hanks",
    "Meryl Streep",
    "Brad Pitt",
    "Julia Roberts",
    "Leonardo DiCaprio",
    "Scarlett Johansson",
    "Denzel Washington",
    "Sandra Bullock",
    "Matt Damon",
    "Nicole Kidman",
    "Keanu Reeves",
    "Charlize Theron",
    "Will Smith",
    "Cate Blanchett",
    "George Clooney",
    "Natalie Portman",
    "Harrison Ford",
    "Anne Hathaway",
    "Christian Bale",
    "Amy Adams",
    "Ryan Gosling",
    "Emma Stone",
    "Morgan Freeman",
    "Jennifer Lawrence",
    "Robert Downey Jr.",
    "Viola Davis",
    "Ben Affleck",
    "Cameron Diaz",
    "Jodie Foster",
    "Chris Evans",
)

SHOW_DICTIONARY = (
    "Поле чудес",
    "Утренняя звезда",
    "Любовь с первого взгляда",
    "Зов джунглей",
    "Счастливый случай",
    "Сам себе режиссер",
    "Джентльмен-шоу",
    "Городок",
    "Маски-шоу",
    "Каламбур",
    "Акулы пера",
    "Смак",
    "Угадай мелодию",
    "До 16 и старше",
    "Тема",
    "Час пик",
    "Добрый вечер",
    "Империя страсти",
    "Моя семья",
    "Куклы",
    "Аншлаг",
    "Оба-на!",
    "В мире людей",
    "Про это",
    "Музыкальный ринг",
    "Сто к одному",
    "Что? Где? Когда?",
    "Пока все дома",
    "Утренняя почта",
    "Взгляд",
)

FORMAT_DICTIONARY = (
    "Болт",
    "Винт",
    "Штифт",
    "Шкив",
    "Ролик",
    "Шток",
    "Фланец",
    "Клапан",
    "Поршень",
    "Шайба",
    "Втулка",
    "Шплинт",
    "Палец",
    "Хомут",
    "Кронштейн",
    "Муфта",
    "Шестерня",
    "Цанга",
    "Фиксатор",
    "Резец",
    "Патрон",
    "Шпиндель",
    "Ротор",
    "Статор",
    "Тавотница",
    "Рессора",
    "Пружина",
    "Сальник",
    "Ниппель",
    "Шпонка",
)

BRAND_DICTIONARY = (
    "Weyland-Yutani",
    "Cyberdyne Systems",
    "Tyrell Corporation",
    "InGen",
    "Oceanic Airlines",
    "Umbrella Corporation",
    "Soylent Industries",
    "Virtucon",
    "MomCorp",
    "Massive Dynamic",
    "Buy n Large",
    "Stark Industries",
    "LexCorp",
    "Oscorp",
    "Globex Corporation",
    "Wonka Industries",
    "Clampett Oil",
    "Dunder Mifflin Infinity",
    "Bluth Company",
    "Duff Brewing",
    "Monsters Inc.",
    "Good Burger Holdings",
    "Nakatomi Trading",
    "Aperture Science",
    "Blue Sun",
    "Morley Tobacco",
    "Acme Industries",
    "Gringotts Ventures",
    "Pied Piper Media",
    "Hooli Pictures",
)


def _stable_token(kind: str, raw: str, *, version: str) -> str:
    payload = f"{version}:{kind}:{raw}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:8]


def _stable_index(kind: str, raw: str, *, version: str, size: int) -> int:
    payload = f"{version}:{kind}:{raw}".encode("utf-8")
    digest = hashlib.sha1(payload).digest()
    return int.from_bytes(digest[:4], "big") % size


def _dictionary_value(kind: str, raw: str, *, version: str, items: tuple[str, ...]) -> str:
    value = str(raw or "").strip()
    if not value:
        return value
    return items[_stable_index(kind, value, version=version, size=len(items))]


def _mask_value(kind: str, raw: str, *, version: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return value
    if kind == "person":
        return _dictionary_value(kind, value, version=version, items=DESIGNER_DICTIONARY)
    if kind == "group":
        return _dictionary_value(kind, value, version=version, items=SHOW_DICTIONARY)
    if kind == "brand":
        return _dictionary_value(kind, value, version=version, items=BRAND_DICTIONARY)
    if kind == "format":
        return _dictionary_value(kind, value, version=version, items=FORMAT_DICTIONARY)
    if kind == "customer":
        return _dictionary_value(kind, value, version=version, items=BRAND_DICTIONARY)
    if kind == "filename":
        token = _stable_token(kind, value, version=version)
        return f"file-{token}"
    if kind == "preview":
        token = _stable_token(kind, value, version=version)
        return f"preview-{token}"
    if kind == "history":
        show = _dictionary_value("history_show", value, version=version, items=SHOW_DICTIONARY)
        format_name = _dictionary_value("history_format", value, version=version, items=FORMAT_DICTIONARY)
        return f"Согласование по проекту «{show}», формат {format_name}"
    if kind == "title":
        brand = _dictionary_value("title_brand", value, version=version, items=BRAND_DICTIONARY)
        show = _dictionary_value("title_show", value, version=version, items=SHOW_DICTIONARY)
        format_name = _dictionary_value("title_format", value, version=version, items=FORMAT_DICTIONARY)
        return f"{brand} [{show}] {format_name}"
    token = _stable_token(kind, value, version=version)
    return f"masked-{token}"


def _apply_mask(payload: dict[str, Any], *, version: str) -> dict[str, Any]:
    masked = json.loads(json.dumps(payload, ensure_ascii=False))
    filters = dict(masked.get("filters", {}) or {})
    if str(filters.get("designer") or "").strip():
        filters["designer"] = _mask_value("person", str(filters.get("designer") or ""), version=version)
    masked["filters"] = filters

    entities = dict(masked.get("entities", {}) or {})
    people = []
    for item in list(entities.get("people", []) or []):
        row = dict(item or {})
        row["name"] = _mask_value("person", str(row.get("name") or ""), version=version)
        people.append(row)
    groups = []
    for item in list(entities.get("groups", []) or []):
        row = dict(item or {})
        row["name"] = _mask_value("group", str(row.get("name") or ""), version=version)
        groups.append(row)
    entities["people"] = people
    entities["groups"] = groups
    masked["entities"] = entities

    tasks = []
    for item in list(masked.get("tasks", []) or []):
        row = dict(item or {})
        row["title"] = _mask_value("title", str(row.get("title") or ""), version=version)
        row["brand"] = _mask_value("brand", str(row.get("brand") or ""), version=version)
        row["format_"] = _mask_value("format", str(row.get("format_") or ""), version=version)
        row["customer"] = _mask_value("customer", str(row.get("customer") or ""), version=version)
        row["history"] = _mask_value("history", str(row.get("history") or ""), version=version)
        attachments = []
        for attachment in list(row.get("attachments", []) or []):
            masked_attachment = dict(attachment or {})
            masked_attachment["filename"] = _mask_value(
                "filename", str(masked_attachment.get("filename") or ""), version=version
            )
            masked_attachment["uploadedBy"] = _mask_value(
                "person", str(masked_attachment.get("uploadedBy") or ""), version=version
            )
            masked_attachment["preview"] = _mask_value(
                "preview", str(masked_attachment.get("preview") or ""), version=version
            )
            attachments.append(masked_attachment)
        row["attachments"] = attachments
        tasks.append(row)
    masked["tasks"] = tasks
    return masked


def mask_frontend_payload(
    payload: dict[str, Any],
    access: AccessContext,
    *,
    dictionary_version: str,
    metrics_client: Any = None,
    metrics_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not access.masked:
        return dict(payload)
    started = perf_counter()
    masked = _apply_mask(payload, version=str(dictionary_version or "v1").strip() or "v1")
    if metrics_client is not None:
        metrics_client.timing("dtm.api.masking_ms", (perf_counter() - started) * 1000.0, labels=dict(metrics_labels or {}))
    return masked

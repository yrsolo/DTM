from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd


def is_nullish(value: Any) -> bool:
    if value is None:
        return True
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(result, (list, tuple)):
        return all(result)
    if hasattr(result, "all"):
        try:
            return bool(result.all())
        except Exception:
            return False
    return bool(result)


def normalize_text(value: Any, strip: bool = True) -> str:
    if is_nullish(value):
        return ""
    text = value if isinstance(value, str) else str(value)
    return text.strip() if strip else text


@dataclass(frozen=True)
class TaskRowContract:
    brand: str
    format_: str
    project_name: str
    customer: str
    designer: str
    raw_timing: str
    status: str
    color: Any
    color_status: str
    name: str
    task_id: Any

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any], field_map: Mapping[str, str]) -> "TaskRowContract":
        return cls(
            brand=normalize_text(row.get(field_map["brand"])),
            format_=normalize_text(row.get(field_map["format_"])),
            project_name=normalize_text(row.get(field_map["project_name"])),
            customer=normalize_text(row.get(field_map["customer"])),
            designer=normalize_text(row.get(field_map["designer"])),
            raw_timing=normalize_text(row.get(field_map["raw_timing"]), strip=False),
            status=normalize_text(row.get(field_map["status"])),
            color=row.get(field_map["color"], None),
            color_status=normalize_text(row.get(field_map["color_status"])),
            name=normalize_text(row.get(field_map["name"])),
            task_id=row.get(field_map["task_id"], None),
        )

    def to_task_kwargs(self) -> dict[str, Any]:
        return {
            "brand": self.brand,
            "format_": self.format_,
            "project_name": self.project_name,
            "customer": self.customer,
            "designer": self.designer,
            "raw_timing": self.raw_timing,
            "status": self.status,
            "color": self.color,
            "color_status": self.color_status,
            "name": self.name,
            "task_id": self.task_id,
        }


@dataclass(frozen=True)
class PersonRowContract:
    person_id: str
    name: str
    email: str
    telegram_id: str
    chat_id: str
    info: str
    position: str
    vacation: str

    @classmethod
    def from_mapping(
        cls, row: Mapping[str, Any], field_map: Mapping[str, str]
    ) -> "PersonRowContract":
        return cls(
            person_id=normalize_text(row.get(field_map["person_id"])),
            name=normalize_text(row.get(field_map["name"])),
            email=normalize_text(row.get(field_map["email"])),
            telegram_id=normalize_text(row.get(field_map["telegram_id"])),
            chat_id=normalize_text(row.get(field_map["chat_id"])),
            info=normalize_text(row.get(field_map["info"]), strip=False),
            position=normalize_text(row.get(field_map["position"])).lower(),
            vacation=normalize_text(row.get(field_map["vacation"])).lower(),
        )

    def to_person_kwargs(self) -> dict[str, str]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "email": self.email,
            "telegram_id": self.telegram_id,
            "chat_id": self.chat_id,
            "info": self.info,
            "position": self.position,
            "vacation": self.vacation,
        }

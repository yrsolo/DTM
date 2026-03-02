"""Build deterministic hash basis from source rows."""

from __future__ import annotations

from typing import Any, Iterable


DEFAULT_HASH_FIELDS = (
    "id",
    "brand",
    "format_",
    "project_name",
    "customer",
    "designer",
    "raw_timing",
    "status",
)


def build_hash_basis(
    rows: Iterable[dict[str, Any]],
    fields: tuple[str, ...] = DEFAULT_HASH_FIELDS,
    row_id_field: str = "id",
) -> list[dict[str, str]]:
    """Return normalized hash basis records for source hash computation.

    Output is deterministic:
    - each selected field converted to stripped string
    - records sorted by row id
    """
    normalized: list[dict[str, str]] = []
    for row in rows:
        record: dict[str, str] = {}
        row_id = str(row.get(row_id_field, "")).strip()
        record[row_id_field] = row_id
        for field in fields:
            record[field] = str(row.get(field, "")).strip()
        normalized.append(record)

    return sorted(normalized, key=lambda item: item.get(row_id_field, ""))


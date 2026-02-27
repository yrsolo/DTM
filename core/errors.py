from __future__ import annotations

from dataclasses import dataclass


class DataQualityError(ValueError):
    """Base class for input data quality failures."""


@dataclass(frozen=True)
class MissingRequiredColumnsError(DataQualityError):
    entity_name: str
    spreadsheet_name: str
    sheet_name: str
    missing_columns: tuple[str, ...]
    field_map_name: str

    def __str__(self) -> str:
        missing_str = ", ".join(self.missing_columns)
        return (
            f"Missing required {self.entity_name} columns in "
            f"'{self.spreadsheet_name}/{self.sheet_name}': {missing_str}. "
            f"Check source sheet headers against config.{self.field_map_name}."
        )

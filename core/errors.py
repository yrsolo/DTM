"""Domain-level error contracts for data quality and parsing issues."""

from __future__ import annotations

from dataclasses import dataclass


class DataQualityError(ValueError):
    """Base class for input data quality failures."""


@dataclass(frozen=True)
class MissingRequiredColumnsError(DataQualityError):
    """Raised when required headers are missing in an input worksheet."""

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


@dataclass(frozen=True)
class RowValidationIssue:
    """Represents a non-fatal malformed input row skipped during parsing."""

    entity_name: str
    row_number: int
    reason: str
    row_id: str = ""

    def __str__(self) -> str:
        suffix = f" [row_id={self.row_id}]" if self.row_id else ""
        return f"Skipped malformed {self.entity_name} row {self.row_number}: {self.reason}{suffix}"


@dataclass(frozen=True)
class TimingParseIssue:
    """Represents a non-fatal timing parser issue for one input row."""

    row_number: int
    timing_line: str
    normalized_date: str
    error: str

    def __str__(self) -> str:
        return (
            f"Timing parse issue at row {self.row_number}: "
            f"date='{self.normalized_date}', line='{self.timing_line}', error='{self.error}'"
        )

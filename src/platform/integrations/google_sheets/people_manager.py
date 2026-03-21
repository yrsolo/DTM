"""Google Sheets backed people manager adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from src.core.contracts import PersonRowContract
from src.core.errors import MissingRequiredColumnsError, RowValidationIssue
from src.core.models.people import Designer, Person
from src.config.loader import load_config

if TYPE_CHECKING:
    from src.platform.integrations.google_sheets.service import GoogleSheetInfo, GoogleSheetsService


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("ascii", "replace").decode("ascii"))


class PeopleManager:
    """Manager for loading and querying people from source sheets."""

    def __init__(
        self,
        people: list[Person] | None = None,
        service: GoogleSheetsService | None = None,
        sheet_info: GoogleSheetInfo | None = None,
        people_field_map: Mapping[str, str] | None = None,
    ) -> None:
        cfg = load_config()
        self.people: dict[str, Person] = {}
        if people:
            self.people = {person.id: person for person in people if person.id}

        self.service = service
        self.sheet_info = sheet_info
        self.people_field_map = dict(people_field_map or cfg.tables.field_maps.get("people", {}))
        self.df = None
        self.row_issues: list[RowValidationIssue] = []

    def _load(self) -> None:
        if not self.people:
            self._load_people_from_sheet()

    def _load_people_from_sheet(self) -> dict[str, Person]:
        if self.service is None or self.sheet_info is None:
            return self.people

        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name("people")
        self.df = self.service.get_dataframe(spreadsheet_name, sheet_name, worksheet_range="A1:Z100")
        self._validate_required_columns(self.df, spreadsheet_name, sheet_name)
        self.row_issues = []
        for index, row in self.df.iterrows():
            row_number = int(index) + 2
            try:
                person = self._create_person(row.to_dict())
            except (TypeError, ValueError, KeyError) as exc:
                self._record_row_issue("people", row_number, f"mapping failure: {exc}")
                continue
            if not person.id:
                self._record_row_issue("people", row_number, "missing person_id")
                continue
            if not person.name:
                self._record_row_issue("people", row_number, "missing name", row_id=person.id)
                continue
            if person.id in self.people:
                self._record_row_issue("people", row_number, "duplicate person_id", row_id=person.id)
                continue
            self.people[person.id] = person
        return self.people

    def _validate_required_columns(self, df: Any, spreadsheet_name: str, sheet_name: str) -> None:
        required_columns = PersonRowContract.required_columns(self.people_field_map)
        missing = sorted(col for col in required_columns if col not in df.columns)
        if missing:
            raise MissingRequiredColumnsError(
                entity_name="people",
                spreadsheet_name=spreadsheet_name,
                sheet_name=sheet_name,
                missing_columns=tuple(missing),
                field_map_name="PEOPLE_FIELD_MAP",
            )

    def _create_person(self, person_row: dict[str, Any]) -> Person:
        contract = PersonRowContract.from_mapping(person_row, self.people_field_map)
        person_kwargs = contract.to_person_kwargs()
        if contract.position == "дизайнер":
            return Designer(**person_kwargs)
        return Person(**person_kwargs)

    def _record_row_issue(self, entity_name: str, row_number: int, reason: str, row_id: str = "") -> None:
        issue = RowValidationIssue(
            entity_name=entity_name,
            row_number=row_number,
            reason=reason,
            row_id=row_id,
        )
        self.row_issues.append(issue)
        _safe_print(str(issue))

    def get_person(self, name: str) -> Person | None:
        self._load()
        persons = [person for person in self.people.values() if person.name == name]
        return persons[0] if persons else None

    def get_designers(self) -> list[Designer]:
        self._load()
        return [person for person in self.people.values() if isinstance(person, Designer)]


from typing import List
from utils.service import GoogleSheetsService, GoogleSheetInfo
from config import PEOPLE_FIELD_MAP
from core.contracts import PersonRowContract, normalize_text
from core.errors import MissingRequiredColumnsError, RowValidationIssue


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("ascii", "replace").decode("ascii"))


class Person:
    """ Человек"""

    def __init__(self, person_id, name, email, position, telegram_id, chat_id, info, vacation, tg_bot=None, **kwargs):
        self.id = normalize_text(person_id)
        self.name = normalize_text(name)
        self.email = normalize_text(email)
        self.telegram_id = normalize_text(telegram_id)
        self.chat_id = normalize_text(chat_id)
        self.tg_bot = tg_bot
        self.info = normalize_text(info, strip=False)
        self.position = normalize_text(position).lower()
        self.vacation = normalize_text(vacation).lower()
        self.tasks = []

    def __repr__(self):
        return f'{self.name}'

    def send_message(self, message, to_chat=True):
        if to_chat:
            self.tg_bot.send_message(self.chat_id, message)
        else:
            self.tg_bot.send_message(self.telegram_id, message)


class Designer(Person):
    """ Дизайнер """

    def __repr__(self):
        return f"Designer({self.name})"


class PeopleManager:
    """Класс для работы с людьми."""

    def __init__(self, people: List[Person] = None, service: GoogleSheetsService = None,
                 sheet_info: GoogleSheetInfo = None):
        self.people = dict()
        if people:
            self.people = {person.id: person for person in people if person.id}

        self.service = service
        self.sheet_info = sheet_info
        self.df = None
        self.row_issues: List[RowValidationIssue] = []

    def _load(self):
        if self.people == {}:
            self._load_people_from_sheet()

    def _load_people_from_sheet(self):
        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name('people')
        self.df = self.service.get_dataframe(spreadsheet_name, sheet_name, worksheet_range='A1:Z100')
        self._validate_required_columns(self.df, spreadsheet_name, sheet_name)
        self.row_issues = []
        for i, row in self.df.iterrows():
            row_number = int(i) + 2
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

    def _validate_required_columns(self, df, spreadsheet_name, sheet_name):
        required_columns = PersonRowContract.required_columns(PEOPLE_FIELD_MAP)
        missing = sorted(col for col in required_columns if col not in df.columns)
        if missing:
            raise MissingRequiredColumnsError(
                entity_name="people",
                spreadsheet_name=spreadsheet_name,
                sheet_name=sheet_name,
                missing_columns=tuple(missing),
                field_map_name="PEOPLE_FIELD_MAP",
            )

    def _create_person(self, person):
        contract = PersonRowContract.from_mapping(person, PEOPLE_FIELD_MAP)
        person_kwargs = contract.to_person_kwargs()
        if contract.position == "\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440":
            person = Designer(**person_kwargs)
        else:
            person = Person(**person_kwargs)
        return person

    def _record_row_issue(self, entity_name: str, row_number: int, reason: str, row_id: str = ""):
        issue = RowValidationIssue(
            entity_name=entity_name,
            row_number=row_number,
            reason=reason,
            row_id=row_id,
        )
        self.row_issues.append(issue)
        _safe_print(str(issue))

    def get_person(self, name):
        self._load()
        persons = [person for person in self.people.values() if person.name == name]
        return persons[0] if persons else None

    def get_designers(self):
        self._load()
        return [person for person in self.people.values() if isinstance(person, Designer)]


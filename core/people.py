from typing import List
import pandas as pd
from utils.service import GoogleSheetsService, GoogleSheetInfo
from config import PEOPLE_FIELD_MAP


def _is_nullish(value) -> bool:
    if value is None:
        return True
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if hasattr(result, "all"):
        try:
            return bool(result.all())
        except Exception:
            return False
    return bool(result)


def _normalize_text(value, strip: bool = True) -> str:
    if _is_nullish(value):
        return ""
    text = value if isinstance(value, str) else str(value)
    return text.strip() if strip else text


class Person:
    """ Человек"""

    def __init__(self, person_id, name, email, position, telegram_id, chat_id, info, vacation, tg_bot=None, **kwargs):
        self.id = _normalize_text(person_id)
        self.name = _normalize_text(name)
        self.email = _normalize_text(email)
        self.telegram_id = _normalize_text(telegram_id)
        self.chat_id = _normalize_text(chat_id)
        self.tg_bot = tg_bot
        self.info = _normalize_text(info, strip=False)
        self.position = _normalize_text(position).lower()
        self.vacation = _normalize_text(vacation).lower()
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

    def _load(self):
        if self.people == {}:
            self._load_people_from_sheet()

    def _load_people_from_sheet(self):
        spreadsheet_name = self.sheet_info.spreadsheet_name
        sheet_name = self.sheet_info.get_sheet_name('people')
        self.df = self.service.get_dataframe(spreadsheet_name, sheet_name, worksheet_range='A1:Z100')
        for i, row in self.df.iterrows():
            person = row.to_dict()
            person = self._create_person(person)
            self.people[person.id] = person
        return self.people

    def _create_person(self, person):
        person = {key: person.get(value, None) for key, value in PEOPLE_FIELD_MAP.items()}
        if _normalize_text(person.get('position')).lower() == 'дизайнер':
            person = Designer(**person)
        else:
            person = Person(**person)
        return person

    def get_person(self, name):
        self._load()
        persons = [person for person in self.people.values() if person.name == name]
        return persons[0] if persons else None

    def get_designers(self):
        self._load()
        return [person for person in self.people.values() if isinstance(person, Designer)]

from typing import List
from utils.service import GoogleSheetsService, GoogleSheetInfo
from config import PEOPLE_FIELD_MAP


class Person:
    """ Человек"""

    def __init__(self, person_id, name, email, position, telegram_id, chat_id, info, vacation, tg_bot=None, **kwargs):
        self.id = person_id
        self.name = name
        self.email = email
        self.telegram_id = telegram_id
        self.chat_id = chat_id
        self.tg_bot = tg_bot
        self.info = info
        self.position = position
        self.vacation = vacation
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
            self.people = {person.id: self.people[person.id] for person in people}

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
        person = {key: person[value] for key, value in PEOPLE_FIELD_MAP.items()}
        if person['position'] == 'дизайнер':
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
        return [person for person in self.people if isinstance(person, Designer)]

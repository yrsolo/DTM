"""Google Sheets adapters package."""

from src.adapters.google_sheets.people_manager import PeopleManager
from src.adapters.google_sheets.task_repository import GoogleSheetsTaskRepository

__all__ = ["GoogleSheetsTaskRepository", "PeopleManager"]

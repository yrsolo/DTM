"""Google Sheets adapters package."""

from src.platform.integrations.google_sheets.people_manager import PeopleManager
from src.platform.integrations.google_sheets.task_repository import GoogleSheetsTaskRepository

__all__ = ["GoogleSheetsTaskRepository", "PeopleManager"]

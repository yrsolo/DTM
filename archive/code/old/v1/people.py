"""People compatibility shim."""

from __future__ import annotations

from core.models.people import Designer, Person
from src.adapters.google_sheets.people_manager import PeopleManager

__all__ = ["Person", "Designer", "PeopleManager"]

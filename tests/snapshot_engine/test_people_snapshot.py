from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.model import PeopleSnapshot, PersonView
from src.snapshot_engine.serialization import people_from_dict, people_to_dict
from src.snapshot_engine.stores import s3_store
from src.snapshot_engine.update_job import PeopleSnapshotUpdater


class _FakeJsonStore:
    def __init__(self) -> None:
        self.data = {}

    def get(self, key: str):
        return self.data.get(key)

    def put(self, key: str, payload):
        self.data[key] = payload


class _FakePeopleStore:
    def __init__(self) -> None:
        self.snapshot = None

    def get(self):
        return self.snapshot

    def put(self, snapshot):
        self.snapshot = snapshot


class _FakeSource:
    def read_worksheet_values(self, sheet_key: str, worksheet_range: str):  # noqa: ANN001
        _ = worksheet_range
        if sheet_key != "people":
            return []
        return [
            ["Id", "Имя", "Телеграмм chat_id", "Отпуск", "Должность"],
            ["p1", "Иван Иванов", "-1001", "", "designer"],
            ["p2", "Мария Петрова", "", "да", "designer"],
        ]


class PeopleSnapshotTestCase(unittest.TestCase):
    def test_people_roundtrip(self) -> None:
        snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={
                "дизайнер": PersonView(
                    name="Дизайнер",
                    chat_id="-1001",
                    vacation="нет",
                    position="designer",
                    person_id="p1",
                )
            },
        )
        restored = people_from_dict(people_to_dict(snapshot))
        self.assertIn("дизайнер", restored.people_by_name)
        self.assertEqual(restored.people_by_name["дизайнер"].chat_id, "-1001")

    def test_s3_people_store_get_put(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3PeopleStore(base, "snapshots/test/people/default.json")
        snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={"a": PersonView(name="A", chat_id="-1", vacation="", position="designer")},
        )
        store.put(snapshot)
        loaded = store.get()
        self.assertIsNotNone(loaded)
        self.assertIn("a", loaded.people_by_name)

    def test_people_updater_reads_people_sheet(self) -> None:
        people_store = _FakePeopleStore()
        updater = PeopleSnapshotUpdater(
            people_store=people_store,
            source_id="sheet:test:people",
            people_field_map={
                "person_id": "Id",
                "name": "Имя",
                "chat_id": "Телеграмм chat_id",
                "vacation": "Отпуск",
                "position": "Должность",
            },
        )
        snapshot = updater.run(_FakeSource())
        self.assertIn("иван иванов", snapshot.people_by_name)
        self.assertEqual(snapshot.people_by_name["иван иванов"].chat_id, "-1001")
        self.assertIn("мария петрова", snapshot.people_by_name)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.snapshot_engine.engine import SnapshotEngine
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


class _NoopStore:
    def get(self):
        return None

    def put(self, _value):
        return None

    def get_snapshot(self):
        return None

    def put_snapshot(self, _value):
        return None


class _FakeSource:
    def read_worksheet_values(self, sheet_key: str, worksheet_range: str):  # noqa: ANN001
        _ = worksheet_range
        if sheet_key != "people":
            return []
        return [
            [
                "Id",
                "Имя",
                "Должность",
                "Почта",
                "Телеграмм",
                "Телеграмм id",
                "Телеграмм chat_id",
                "Информация",
                "Отпуск",
                "Телефон",
                "почта",
            ],
            ["p1", "Иван Иванов", "designer", "ivan@example.com", "@ivan", "1001", "-1001", "lead", "", "79030000000", "ivan@corp.local"],
            ["p2", "Мария Петрова", "designer", "", "@maria", "1002", "", "", "да", "", ""],
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
                    email="designer@example.com",
                    email_secondary="designer@corp.local",
                    telegram="@designer",
                    telegram_id="1001",
                    info="lead",
                    phone="79030000000",
                    attributes={"email": "designer@example.com", "phone": "79030000000"},
                )
            },
        )
        restored = people_from_dict(people_to_dict(snapshot))
        self.assertIn("дизайнер", restored.people_by_name)
        self.assertEqual(restored.people_by_name["дизайнер"].chat_id, "-1001")
        self.assertEqual(restored.people_by_name["дизайнер"].email, "designer@example.com")
        self.assertEqual(restored.people_by_name["дизайнер"].phone, "79030000000")
        self.assertEqual(restored.people_by_name["дизайнер"].attributes["email"], "designer@example.com")

    def test_s3_people_store_get_put(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3PeopleStore(base, "snapshots/test/people/default.json")
        snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={"a": PersonView(name="A", chat_id="-1", vacation="", position="designer", email="a@example.com")},
        )
        store.put(snapshot)
        loaded = store.get()
        self.assertIsNotNone(loaded)
        self.assertIn("a", loaded.people_by_name)

    def test_people_updater_reads_all_mapped_people_columns(self) -> None:
        people_store = _FakePeopleStore()
        updater = PeopleSnapshotUpdater(
            people_store=people_store,
            source_id="sheet:test:people",
            people_field_map={
                "person_id": "Id",
                "name": "Имя",
                "position": "Должность",
                "email": "Почта",
                "telegram": "Телеграмм",
                "telegram_id": "Телеграмм id",
                "chat_id": "Телеграмм chat_id",
                "info": "Информация",
                "vacation": "Отпуск",
                "phone": "Телефон",
                "email_secondary": "почта",
            },
        )
        snapshot = updater.run(_FakeSource())
        self.assertIn("иван иванов", snapshot.people_by_name)
        self.assertEqual(snapshot.people_by_name["иван иванов"].chat_id, "-1001")
        self.assertEqual(snapshot.people_by_name["иван иванов"].email, "ivan@example.com")
        self.assertEqual(snapshot.people_by_name["иван иванов"].telegram_id, "1001")
        self.assertEqual(snapshot.people_by_name["иван иванов"].phone, "79030000000")
        self.assertEqual(snapshot.people_by_name["иван иванов"].email_secondary, "ivan@corp.local")
        self.assertEqual(snapshot.people_by_name["иван иванов"].attributes["telegram"], "@ivan")
        self.assertIn("мария петрова", snapshot.people_by_name)

    def test_snapshot_engine_lookup_helpers_use_people_registry(self) -> None:
        people_store = _FakePeopleStore()
        people_store.put(
            PeopleSnapshot(
                source_id="sheet:test:people",
                fetched_at_utc=datetime.now(timezone.utc),
                people_by_name={
                    "иван иванов": PersonView(
                        name="Иван Иванов",
                        person_id="p1",
                        email="ivan@example.com",
                        email_secondary="ivan@corp.local",
                        telegram_id="1001",
                        chat_id="-1001",
                    )
                },
            )
        )
        engine = SnapshotEngine(
            raw_cache=_NoopStore(),
            prep_cache=_NoopStore(),
            extra_store=_NoopStore(),
            people_store=people_store,
            response_cache_store=_NoopStore(),
            query_engine=None,
            prep_builder=None,
            update_job_factory=lambda _source: None,
            people_update_job_factory=lambda _source: None,
        )

        self.assertEqual(engine.find_by_email("ivan@example.com").person_id, "p1")
        self.assertEqual(engine.find_by_email("ivan@corp.local").person_id, "p1")
        self.assertEqual(engine.find_by_telegram_id("1001").person_id, "p1")
        self.assertEqual(engine.find_by_chat_id("-1001").person_id, "p1")
        self.assertEqual(engine.find_by_name("Иван Иванов").person_id, "p1")


if __name__ == "__main__":
    unittest.main()

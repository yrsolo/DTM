from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.contexts.snapshot.internal.engine.engine import SnapshotEngine
from src.contexts.snapshot.internal.engine.model import PeopleSnapshot, PersonView
from src.contexts.snapshot.internal.engine.serialization import people_from_dict, people_to_dict
from src.contexts.snapshot.internal.engine.stores import s3_store
from src.contexts.snapshot.internal.engine.update_job import PeopleSnapshotUpdater


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
                "\u0418\u043c\u044f",
                "\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c",
                "\u041f\u043e\u0447\u0442\u0430",
                "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c",
                "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c id",
                "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c chat_id",
                "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f",
                "\u041e\u0442\u043f\u0443\u0441\u043a",
                "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
                "\u041f\u043e\u0447\u0442\u0430 \u044f\u043d\u0434\u0435\u043a\u0441",
            ],
            ["p1", "\u0418\u0432\u0430\u043d \u0418\u0432\u0430\u043d\u043e\u0432", "designer", "ivan@example.com", "@ivan", "1001", "-1001", "lead", "", "79030000000", "ivan@corp.local"],
            ["p2", "\u041c\u0430\u0440\u0438\u044f \u041f\u0435\u0442\u0440\u043e\u0432\u0430", "designer", "", "@maria", "1002", "", "", "\u0434\u0430", "", ""],
        ]


class PeopleSnapshotTestCase(unittest.TestCase):
    def test_people_roundtrip(self) -> None:
        snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={
                "\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440": PersonView(
                    name="\u0414\u0438\u0437\u0430\u0439\u043d\u0435\u0440",
                    is_active=True,
                    chat_id="-1001",
                    vacation="\u043d\u0435\u0442",
                    position="designer",
                    person_id="p1",
                    contact_email="designer@example.com",
                    yandex_email="designer@yandex.ru",
                    telegram="@designer",
                    telegram_id="1001",
                    info="lead",
                    phone="79030000000",
                    attributes={"contact_email": "designer@example.com", "yandex_email": "designer@yandex.ru", "phone": "79030000000"},
                )
            },
        )
        restored = people_from_dict(people_to_dict(snapshot))
        self.assertIn("\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440", restored.people_by_name)
        self.assertTrue(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].is_active)
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].chat_id, "-1001")
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].contact_email, "designer@example.com")
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].yandex_email, "designer@yandex.ru")
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].phone, "79030000000")
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].attributes["contact_email"], "designer@example.com")
        self.assertEqual(restored.people_by_name["\u0434\u0438\u0437\u0430\u0439\u043d\u0435\u0440"].attributes["yandex_email"], "designer@yandex.ru")

    def test_s3_people_store_get_put(self) -> None:
        base = _FakeJsonStore()
        store = s3_store.S3PeopleStore(base, "snapshots/test/people/default.json")
        snapshot = PeopleSnapshot(
            source_id="sheet:test:people",
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name={"a": PersonView(name="A", chat_id="-1", vacation="", position="designer", contact_email="a@example.com", yandex_email="a@yandex.ru")},
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
                "name": "\u0418\u043c\u044f",
                "position": "\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c",
                "contact_email": "\u041f\u043e\u0447\u0442\u0430",
                "yandex_email": "\u041f\u043e\u0447\u0442\u0430 \u044f\u043d\u0434\u0435\u043a\u0441",
                "telegram": "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c",
                "telegram_id": "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c id",
                "chat_id": "\u0422\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c chat_id",
                "info": "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f",
                "vacation": "\u041e\u0442\u043f\u0443\u0441\u043a",
                "phone": "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
            },
        )
        snapshot = updater.run(_FakeSource())
        self.assertIn("\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432", snapshot.people_by_name)
        self.assertTrue(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].is_active)
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].chat_id, "-1001")
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].contact_email, "ivan@example.com")
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].yandex_email, "ivan@corp.local")
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].telegram_id, "1001")
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].phone, "79030000000")
        self.assertEqual(snapshot.people_by_name["\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432"].attributes["telegram"], "@ivan")
        self.assertIn("\u043c\u0430\u0440\u0438\u044f \u043f\u0435\u0442\u0440\u043e\u0432\u0430", snapshot.people_by_name)
        self.assertFalse(snapshot.people_by_name["\u043c\u0430\u0440\u0438\u044f \u043f\u0435\u0442\u0440\u043e\u0432\u0430"].is_active)

    def test_snapshot_engine_lookup_helpers_use_people_registry(self) -> None:
        people_store = _FakePeopleStore()
        people_store.put(
            PeopleSnapshot(
                source_id="sheet:test:people",
                fetched_at_utc=datetime.now(timezone.utc),
                people_by_name={
                    "\u0438\u0432\u0430\u043d \u0438\u0432\u0430\u043d\u043e\u0432": PersonView(
                        name="\u0418\u0432\u0430\u043d \u0418\u0432\u0430\u043d\u043e\u0432",
                        is_active=True,
                        person_id="p1",
                        contact_email="ivan@example.com",
                        yandex_email="ivan@yandex.ru",
                        telegram_id="1001",
                        chat_id="-1001",
                    )
                },
            )
        )
        engine = SnapshotEngine(
            attachment_bucket="dtm",
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

        self.assertEqual(engine.find_by_yandex_email("ivan@yandex.ru").person_id, "p1")
        self.assertEqual(engine.find_by_email("ivan@yandex.ru").person_id, "p1")
        self.assertEqual(engine.find_by_telegram_id("1001").person_id, "p1")
        self.assertEqual(engine.find_by_chat_id("-1001").person_id, "p1")
        self.assertEqual(engine.find_by_name("\u0418\u0432\u0430\u043d \u0418\u0432\u0430\u043d\u043e\u0432").person_id, "p1")

    def test_infer_person_is_active_uses_safe_markers_only(self) -> None:
        from src.contexts.snapshot.internal.engine.update_job import infer_person_is_active

        self.assertTrue(infer_person_is_active(vacation=".", info=""))
        self.assertTrue(infer_person_is_active(vacation="", info=""))
        self.assertFalse(infer_person_is_active(vacation="да", info=""))
        self.assertFalse(infer_person_is_active(vacation="+", info=""))
        self.assertFalse(infer_person_is_active(vacation="в отпуске", info=""))
        self.assertFalse(infer_person_is_active(vacation="", info="не работает"))
        self.assertFalse(infer_person_is_active(vacation="", info="уволен"))
        self.assertFalse(infer_person_is_active(vacation="", info="❌"))


if __name__ == "__main__":
    unittest.main()

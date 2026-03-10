from __future__ import annotations

import unittest
from datetime import datetime, timezone

from scripts.migrate_extra_store_to_bulk import build_bulk_extra_snapshot_from_legacy
from src.snapshot_engine.model import TaskExtra


class ExtraStoreMigrationTestCase(unittest.TestCase):
    def test_build_bulk_snapshot_from_legacy_keeps_last_duplicate(self) -> None:
        older = TaskExtra(task_id="t1", notes="old", updated_at_utc=datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc))
        newer = TaskExtra(task_id="t1", notes="new", updated_at_utc=datetime(2026, 3, 9, 11, 0, tzinfo=timezone.utc))
        snapshot, report = build_bulk_extra_snapshot_from_legacy(
            [
                ("snapshots/test/extra/t1.json", older),
                ("snapshots/test/extra/t1-dup.json", newer),
            ]
        )
        self.assertEqual(snapshot.items_by_task_id["t1"].notes, "new")
        self.assertEqual(report["objects_scanned"], 2)
        self.assertEqual(report["valid_extras_migrated"], 1)
        self.assertEqual(report["duplicate_task_ids"], ["t1"])


if __name__ == "__main__":
    unittest.main()

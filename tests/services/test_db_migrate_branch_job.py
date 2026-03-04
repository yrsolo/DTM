from __future__ import annotations

import unittest

from src.entrypoints.jobs.db_migrate_branch import run_db_migrate_if_requested


class DbMigrateBranchJobTestCase(unittest.TestCase):
    def test_returns_not_handled_for_other_modes(self) -> None:
        handled, result = run_db_migrate_if_requested(
            mode="timer",
            endpoint="ep",
            database="db",
            sa_json_credentials=None,
            sa_key_file=None,
            run_db_migrate=lambda **kwargs: kwargs,  # noqa: ARG005
        )
        self.assertFalse(handled)
        self.assertIsNone(result)

    def test_runs_migrate_for_db_migrate_mode(self) -> None:
        handled, result = run_db_migrate_if_requested(
            mode="db_migrate",
            endpoint="ep",
            database="db",
            sa_json_credentials="creds",
            sa_key_file="key",
            run_db_migrate=lambda **kwargs: kwargs,
        )
        self.assertTrue(handled)
        self.assertEqual(result["endpoint"], "ep")
        self.assertEqual(result["database"], "db")
        self.assertEqual(result["sa_json_credentials"], "creds")
        self.assertEqual(result["sa_key_file"], "key")


if __name__ == "__main__":
    unittest.main()

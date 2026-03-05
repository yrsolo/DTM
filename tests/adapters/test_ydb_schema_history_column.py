"""Schema migration tests for dtm_tasks.history column."""

from __future__ import annotations

import unittest

from src.adapters.ydb.schema import ensure_tables, ensure_tasks_history_column


class _ClientStub:
    def __init__(self) -> None:
        self.ddl_calls: list[str] = []

    def execute_scheme(self, query: str) -> None:
        self.ddl_calls.append(query)


class _AlreadyExistsClientStub(_ClientStub):
    def execute_scheme(self, query: str) -> None:
        self.ddl_calls.append(query)
        if query.startswith("ALTER TABLE"):
            raise RuntimeError("Column already exists")


class SchemaHistoryColumnTestCase(unittest.TestCase):
    def test_ensure_tables_applies_history_column_migration(self) -> None:
        client = _ClientStub()

        ensure_tables(client)  # type: ignore[arg-type]

        self.assertTrue(any("history Utf8" in query for query in client.ddl_calls))
        self.assertTrue(any(query.startswith("ALTER TABLE `dtm_tasks` ADD COLUMN history Utf8;") for query in client.ddl_calls))

    def test_ensure_history_column_ignores_existing_column_error(self) -> None:
        client = _AlreadyExistsClientStub()

        ensure_tasks_history_column(client)  # type: ignore[arg-type]

        self.assertEqual(len(client.ddl_calls), 1)
        self.assertIn("ADD COLUMN history Utf8", client.ddl_calls[0])


if __name__ == "__main__":
    unittest.main()

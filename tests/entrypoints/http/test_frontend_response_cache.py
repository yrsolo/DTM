from __future__ import annotations

import unittest

from src.entrypoints.http.frontend_response_cache import (
    default_frontend_cache_keys,
    invalidate_default_frontend_responses,
)


class _FakeResponseCacheStore:
    def __init__(self) -> None:
        self.deleted = []

    def delete(self, cache_key: str) -> None:
        self.deleted.append(cache_key)


class _FakeSnapshotEngine:
    def __init__(self, store) -> None:  # noqa: ANN001
        self._store = store

    def get_response_cache_store(self):
        return self._store


class FrontendResponseCacheHelpersTestCase(unittest.TestCase):
    def test_default_frontend_cache_keys_are_exact_four_known_variants(self) -> None:
        self.assertEqual(
            default_frontend_cache_keys(),
            [
                "frontend_v2/default/api/masked",
                "frontend_v2/default/api/full",
                "frontend_v2/default/bff/masked",
                "frontend_v2/default/bff/full",
            ],
        )

    def test_invalidate_default_frontend_responses_deletes_all_known_keys(self) -> None:
        store = _FakeResponseCacheStore()
        invalidate_default_frontend_responses(_FakeSnapshotEngine(store))
        self.assertEqual(store.deleted, default_frontend_cache_keys())

    def test_invalidate_default_frontend_responses_ignores_missing_store(self) -> None:
        invalidate_default_frontend_responses(_FakeSnapshotEngine(None))


if __name__ == "__main__":
    unittest.main()

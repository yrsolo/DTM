from __future__ import annotations

import unittest
from datetime import datetime

from src.contexts.access_api.internal.masking import masking_version_for_hour


class MaskingVersionTestCase(unittest.TestCase):
    def test_masking_version_is_stable_within_same_moscow_hour(self) -> None:
        first = masking_version_for_hour("v1", now=datetime.fromisoformat("2026-03-12T10:05:00+03:00"))
        second = masking_version_for_hour("v1", now=datetime.fromisoformat("2026-03-12T10:59:59+03:00"))
        self.assertEqual(first, second)

    def test_masking_version_changes_on_next_moscow_hour(self) -> None:
        first = masking_version_for_hour("v1", now=datetime.fromisoformat("2026-03-12T10:59:59+03:00"))
        second = masking_version_for_hour("v1", now=datetime.fromisoformat("2026-03-12T11:00:00+03:00"))
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()

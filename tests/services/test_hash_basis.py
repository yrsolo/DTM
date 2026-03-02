"""Unit tests for source hash basis builder."""

from __future__ import annotations

import unittest

from src.services.sync.hash_basis import build_hash_basis
from src.services.sync.hash_gate import compute_source_hash


class HashBasisTestCase(unittest.TestCase):
    def test_deterministic_when_rows_reordered(self) -> None:
        rows_a = [
            {"id": "2", "designer": "B", "raw_timing": "05.03"},
            {"id": "1", "designer": "A", "raw_timing": "04.03"},
        ]
        rows_b = list(reversed(rows_a))
        basis_a = build_hash_basis(rows_a, fields=("designer", "raw_timing"))
        basis_b = build_hash_basis(rows_b, fields=("designer", "raw_timing"))
        self.assertEqual(basis_a, basis_b)
        self.assertEqual(compute_source_hash(basis_a), compute_source_hash(basis_b))

    def test_hash_changes_when_selected_field_changes(self) -> None:
        rows = [{"id": "1", "designer": "A", "raw_timing": "04.03"}]
        basis_a = build_hash_basis(rows, fields=("designer", "raw_timing"))
        rows[0]["raw_timing"] = "05.03"
        basis_b = build_hash_basis(rows, fields=("designer", "raw_timing"))
        self.assertNotEqual(compute_source_hash(basis_a), compute_source_hash(basis_b))


if __name__ == "__main__":
    unittest.main()


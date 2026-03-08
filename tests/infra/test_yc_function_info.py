from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.infra.yc_function_info import _load_sa_key


class YcFunctionInfoTestCase(unittest.TestCase):
    def test_load_sa_key_rejects_empty_file_path_without_treating_current_dir_as_key(self) -> None:
        with self.assertRaises(RuntimeError):
            _load_sa_key(None, "")


if __name__ == "__main__":
    unittest.main()

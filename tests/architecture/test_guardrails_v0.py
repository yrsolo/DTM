from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = [
    ROOT / "src" / "entrypoint",
    ROOT / "src" / "platform",
    ROOT / "src" / "contexts",
]


def _python_files(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        result.extend(sorted(path.rglob("*.py")))
    return result


class GuardrailsV0TestCase(unittest.TestCase):
    def test_target_layers_do_not_read_env_directly(self) -> None:
        offenders: list[str] = []
        for file_path in _python_files(TARGET_DIRS):
            content = file_path.read_text(encoding="utf-8")
            if "os.getenv(" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_target_layers_do_not_import_legacy(self) -> None:
        offenders: list[str] = []
        for file_path in _python_files(TARGET_DIRS):
            content = file_path.read_text(encoding="utf-8")
            if "src.legacy" in content or "from src.legacy" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_entrypoint_does_not_import_heavy_adapters_directly(self) -> None:
        heavy_markers = [
            "from src.adapters",
            "import src.adapters",
            "from src.telegram",
            "from src.notify",
            "from src.snapshot_engine",
        ]
        offenders: list[str] = []
        for file_path in _python_files([ROOT / "src" / "entrypoint"]):
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in heavy_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_contexts_do_not_reach_into_other_contexts(self) -> None:
        offenders: list[str] = []
        for file_path in _python_files([ROOT / "src" / "contexts"]):
            content = file_path.read_text(encoding="utf-8")
            for context_name in (
                "access_api",
                "attachments",
                "reminders",
                "rendering",
                "snapshot",
                "telegram_interaction",
            ):
                self_import = f"src.contexts.{context_name}"
                if self_import in content and context_name not in str(file_path):
                    offenders.append(str(file_path.relative_to(ROOT)))
                    break
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

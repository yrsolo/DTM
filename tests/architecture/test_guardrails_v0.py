from __future__ import annotations

from pathlib import Path
import re
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
        if path.is_file():
            if path.suffix == ".py":
                result.append(path)
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

    def test_active_runtime_paths_do_not_import_legacy_namespace(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "app",
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "platform",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "jobs",
            ROOT / "src" / "services",
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
            ROOT / "src" / "entrypoints_adapters",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.legacy" in content or "from src.legacy" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_runtime_paths_do_not_import_archived_legacy_namespace(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "app",
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "platform",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "jobs",
            ROOT / "src" / "services",
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
            ROOT / "src" / "entrypoints_adapters",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.archive.legacy_runtime" in content or "from src.archive.legacy_runtime" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_runtime_paths_do_not_import_legacy_config_package(self) -> None:
        offenders: list[str] = []
        import_patterns = (
            re.compile(r"^\s*from\s+config(?:\s+import|\.)", re.MULTILINE),
            re.compile(r"^\s*import\s+config(?:\s|$|\.)", re.MULTILINE),
        )
        target_paths = [
            ROOT / "src" / "app",
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "platform",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "jobs",
            ROOT / "src" / "services",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if any(pattern.search(content) for pattern in import_patterns):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_default_test_contour_does_not_import_legacy_namespaces(self) -> None:
        offenders: list[str] = []
        import_patterns = (
            re.compile(r"^\s*from\s+src\.legacy(?:\.|\s+import)", re.MULTILINE),
            re.compile(r"^\s*import\s+src\.legacy(?:\.|\s|$)", re.MULTILINE),
            re.compile(r"^\s*from\s+src\.archive\.legacy_runtime(?:\.|\s+import)", re.MULTILINE),
            re.compile(r"^\s*import\s+src\.archive\.legacy_runtime(?:\.|\s|$)", re.MULTILINE),
        )
        for file_path in _python_files([ROOT / "tests"]):
            content = file_path.read_text(encoding="utf-8")
            if any(pattern.search(content) for pattern in import_patterns):
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

    def test_active_entrypoints_do_not_import_app_bootstrap_directly(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "entrypoints",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "from src.app.bootstrap import" in content or "import src.app.bootstrap" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_contexts_do_not_reach_into_other_contexts(self) -> None:
        offenders: list[str] = []
        allowed_cross_imports = {
            "attachments": {
                "src.contexts.snapshot.public",
                "src.contexts.snapshot.contracts",
            },
            "reminders": {
                "src.contexts.snapshot.public",
                "src.contexts.snapshot.contracts",
            },
            "rendering": {
                "src.contexts.snapshot.public",
                "src.contexts.snapshot.contracts",
            },
            "telegram_interaction": {
                "src.contexts.snapshot.public",
                "src.contexts.snapshot.contracts",
            },
        }
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
                owner_context = next(
                    (name for name in ("access_api", "attachments", "reminders", "rendering", "snapshot", "telegram_interaction") if f"\\{name}\\" in str(file_path)),
                    "",
                )
                if self_import in content and context_name not in str(file_path):
                    allowed = allowed_cross_imports.get(owner_context, set())
                    if any(marker in content for marker in allowed):
                        cleaned = content
                        for marker in allowed:
                            cleaned = cleaned.replace(marker, "")
                        if self_import not in cleaned:
                            continue
                    offenders.append(str(file_path.relative_to(ROOT)))
                    break
        self.assertEqual(offenders, [])

    def test_rendering_depends_only_on_snapshot_public_contracts(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "contexts" / "rendering",
            ROOT / "src" / "jobs" / "render_timeline_job.py",
            ROOT / "src" / "jobs" / "render_designers_job.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "from src.snapshot_engine" in content or "import src.snapshot_engine" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
            if "from src.snapshot_engine.model" in content or "import src.snapshot_engine.model" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_snapshot_engine_imports_stay_inside_snapshot_boundary(self) -> None:
        offenders: list[str] = []
        allowed_roots = {
            ROOT / "src" / "snapshot_engine",
            ROOT / "src" / "contexts" / "snapshot",
        }
        for file_path in _python_files([ROOT / "src"]):
            if any(root in file_path.parents or file_path == root for root in allowed_roots):
                continue
            content = file_path.read_text(encoding="utf-8")
            if (
                "from src.snapshot_engine" in content
                or "import src.snapshot_engine" in content
            ):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_render_notify_adapters_import_snapshot_only_through_context_surface(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
            ROOT / "src" / "entrypoints_adapters",
        ]
        allowed_snapshot_imports = {
            "from src.contexts.snapshot.public import",
            "import src.contexts.snapshot.public",
            "from src.contexts.snapshot.contracts import",
            "import src.contexts.snapshot.contracts",
        }
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.snapshot_engine" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
                continue
            for line in content.splitlines():
                if "src.contexts.snapshot" not in line:
                    continue
                if not any(marker in line for marker in allowed_snapshot_imports):
                    offenders.append(str(file_path.relative_to(ROOT)))
                    break
        self.assertEqual(offenders, [])

    def test_platform_queue_bootstrap_does_not_import_jobs_directly(self) -> None:
        file_path = ROOT / "src" / "platform" / "runtime" / "queue_bootstrap.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.jobs", content)
        self.assertNotIn("import src.jobs", content)


if __name__ == "__main__":
    unittest.main()

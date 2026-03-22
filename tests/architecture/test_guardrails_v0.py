from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = [
    ROOT / "src" / "entrypoint",
    ROOT / "src" / "platform",
    ROOT / "src" / "contexts",
    ROOT / "src" / "core",
]

ALLOWED_ENV_READ_FILES = {
    ROOT / "src" / "platform" / "bootstrap.py",
}


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
            if file_path in ALLOWED_ENV_READ_FILES:
                continue
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
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "archive.code.legacy_runtime" in content or "from archive.code.legacy_runtime" in content:
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
            re.compile(r"^\s*from\s+archive\.code\.legacy_runtime(?:\.|\s+import)", re.MULTILINE),
            re.compile(r"^\s*import\s+archive\.code\.legacy_runtime(?:\.|\s|$)", re.MULTILINE),
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
            "from src.contexts.snapshot.internal.engine",
        ]
        offenders: list[str] = []
        for file_path in _python_files([ROOT / "src" / "entrypoint"]):
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in heavy_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_index_does_not_export_bootstrap_mutation_seams(self) -> None:
        file_path = ROOT / "index.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("APP_DEPS", content)
        self.assertNotIn("APP_TRIGGERS", content)
        self.assertNotIn("def _get_app_context", content)

    def test_active_entrypoints_do_not_import_removed_app_bootstrap(self) -> None:
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

    def test_active_code_does_not_import_root_core_package(self) -> None:
        offenders: list[str] = []
        import_patterns = (
            re.compile(r"^\s*from\s+core(?:\.|\s+import)", re.MULTILINE),
            re.compile(r"^\s*import\s+core(?:\.|\s|$)", re.MULTILINE),
        )
        for file_path in _python_files([
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src",
            ROOT / "tests",
            ROOT / "agent",
            ROOT / "scripts",
        ]):
            content = file_path.read_text(encoding="utf-8")
            if any(pattern.search(content) for pattern in import_patterns):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_root_core_package_does_not_exist_as_tracked_python_root(self) -> None:
        path = ROOT / "core"
        if not path.exists():
            return
        tracked_python_files = sorted(
            str(file_path.relative_to(ROOT))
            for file_path in path.rglob("*.py")
        )
        self.assertEqual(tracked_python_files, [])

    def test_active_code_does_not_import_root_utils_package(self) -> None:
        offenders: list[str] = []
        import_patterns = (
            re.compile(r"^\s*from\s+utils(?:\.|\s+import)", re.MULTILINE),
            re.compile(r"^\s*import\s+utils(?:\.|\s|$)", re.MULTILINE),
        )
        for file_path in _python_files([
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src",
            ROOT / "tests",
            ROOT / "agent",
            ROOT / "scripts",
        ]):
            content = file_path.read_text(encoding="utf-8")
            if any(pattern.search(content) for pattern in import_patterns):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_root_utils_package_does_not_exist_as_tracked_python_root(self) -> None:
        path = ROOT / "utils"
        if not path.exists():
            return
        tracked_python_files = sorted(
            str(file_path.relative_to(ROOT))
            for file_path in path.rglob("*.py")
        )
        self.assertEqual(tracked_python_files, [])

    def test_active_runtime_paths_do_not_import_removed_index_dispatcher(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.entrypoints.index_dispatcher" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_contexts_do_not_reach_into_other_contexts(self) -> None:
        offenders: list[str] = []
        allowed_cross_imports = {
            "access_api": {
                "src.contexts.attachments.public",
                "src.contexts.attachments.contracts",
                "src.contexts.snapshot.module",
                "src.contexts.snapshot.contracts",
            },
            "attachments": {
                "src.contexts.snapshot.module",
                "src.contexts.snapshot.contracts",
            },
            "reminders": {
                "src.contexts.snapshot.module",
                "src.contexts.snapshot.contracts",
            },
            "rendering": {
                "src.contexts.snapshot.module",
                "src.contexts.snapshot.contracts",
            },
            "snapshot": {
                "src.contexts.attachments.contracts",
            },
            "telegram_interaction": {
                "src.contexts.snapshot.module",
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
            if "from src.contexts.snapshot.internal.engine" in content or "import src.contexts.snapshot.internal.engine" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
            if "from src.contexts.snapshot.internal.engine.model" in content or "import src.contexts.snapshot.internal.engine.model" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_snapshot_engine_imports_stay_inside_snapshot_boundary(self) -> None:
        offenders: list[str] = []
        allowed_roots = {
            ROOT / "src" / "contexts" / "snapshot",
        }
        for file_path in _python_files([ROOT / "src"]):
            if any(root in file_path.parents or file_path == root for root in allowed_roots):
                continue
            content = file_path.read_text(encoding="utf-8")
            if (
                "from src.contexts.snapshot.internal.engine" in content
                or "import src.contexts.snapshot.internal.engine" in content
            ):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_removed_snapshot_engine_root_does_not_exist(self) -> None:
        path = ROOT / "src" / "snapshot_engine"
        python_files = sorted(path.rglob("*.py")) if path.exists() else []
        self.assertEqual(python_files, [])

    def test_render_notify_adapters_import_snapshot_only_through_context_surface(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
        ]
        allowed_snapshot_imports = {
            "from src.contexts.snapshot.public import",
            "import src.contexts.snapshot.public",
            "from src.contexts.snapshot.contracts import",
            "import src.contexts.snapshot.contracts",
        }
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.contexts.snapshot.internal.engine" in content:
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

    def test_active_paths_use_command_runtime_instead_of_queue_dep_keys(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "contexts",
        ]
        forbidden_markers = (
            'deps.get("command_queue_producer"',
            "deps.get('command_queue_producer'",
            'deps.get("job_status_store"',
            "deps.get('job_status_store'",
            'deps.get("command_worker"',
            "deps.get('command_worker'",
        )
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_platform_bootstrap_does_not_build_attachment_converter_directly(self) -> None:
        file_path = ROOT / "src" / "platform" / "bootstrap.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("DocPreviewConverter", content)
        self.assertNotIn("DocPreviewConverter(", content)

    def test_active_module_first_paths_do_not_import_jobs_directly(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
            ROOT / "src" / "contexts",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "from src.jobs" in content or "import src.jobs" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_removed_jobs_root_does_not_exist(self) -> None:
        path = ROOT / "src" / "jobs"
        python_files = sorted(path.rglob("*.py")) if path.exists() else []
        self.assertEqual(python_files, [])

    def test_removed_historical_test_roots_do_not_exist(self) -> None:
        for relative in [
            "tests/adapters",
            "tests/app",
            "tests/entrypoint",
            "tests/infra",
            "tests/jobs",
            "tests/observability",
            "tests/snapshot_engine",
            "tests/notify",
            "tests/render",
            "tests/telegram",
            "tests/worker",
        ]:
            path = ROOT / relative
            python_files = sorted(path.rglob("*.py")) if path.exists() else []
            self.assertEqual(python_files, [], msg=relative)

    def test_http_entrypoints_do_not_import_attachments_services_directly(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "entrypoints" / "http",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.services.attachments" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_attachment_paths_do_not_import_old_attachments_cluster(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "jobs" / "attach_task_file_job.py",
            ROOT / "src" / "snapshot_engine" / "engine.py",
            ROOT / "src" / "snapshot_engine" / "frontend_v2_payload_builder.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.services.attachments" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_jobs_do_not_import_http_frontend_cache_helpers(self) -> None:
        offenders: list[str] = []
        for file_path in _python_files([ROOT / "src" / "jobs"]):
            content = file_path.read_text(encoding="utf-8")
            if "src.entrypoints.http.frontend_response_cache" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_reminder_and_group_query_paths_do_not_import_old_clusters_directly(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "jobs" / "send_reminders_job.py",
            ROOT / "src" / "jobs" / "group_query_reply_job.py",
            ROOT / "src" / "entrypoints" / "runtime" / "planner_runtime_entry.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "from src.notify" in content or "import src.notify" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
                continue
            if "from src.telegram" in content or "import src.telegram" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_reminders_and_telegram_context_modules_do_not_import_old_clusters(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "contexts" / "reminders" / "module.py",
            ROOT / "src" / "contexts" / "telegram_interaction" / "module.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "from src.notify" in content or "import src.notify" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
                continue
            if "from src.telegram" in content or "import src.telegram" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_rendering_context_module_does_not_import_old_render_cluster(self) -> None:
        file_path = ROOT / "src" / "contexts" / "rendering" / "module.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.render", content)
        self.assertNotIn("import src.render", content)

    def test_attachments_context_module_does_not_import_old_attachments_cluster(self) -> None:
        file_path = ROOT / "src" / "contexts" / "attachments" / "module.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.services.attachments", content)
        self.assertNotIn("import src.services.attachments", content)

    def test_access_api_context_module_does_not_import_old_http_handlers(self) -> None:
        file_path = ROOT / "src" / "contexts" / "access_api" / "module.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.entrypoints.http.frontend_compat_handlers", content)
        self.assertNotIn("from src.entrypoints.http.frontend_v2_handler", content)
        self.assertNotIn("from src.entrypoints.http.info_handler", content)
        self.assertNotIn("from src.entrypoints.http.people_snapshot_handler", content)
        self.assertNotIn("from src.entrypoints.http.task_attachment_read_handler", content)

    def test_access_api_internal_paths_do_not_import_old_frontend_cache_helper(self) -> None:
        file_path = ROOT / "src" / "contexts" / "access_api" / "internal" / "primary_task_list_read_api.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.entrypoints.http.frontend_response_cache", content)
        self.assertNotIn("import src.entrypoints.http.frontend_response_cache", content)

    def test_removed_http_access_api_wrappers_do_not_exist(self) -> None:
        removed_paths = [
            ROOT / "src" / "entrypoints" / "http" / "frontend_compat_handlers.py",
            ROOT / "src" / "entrypoints" / "http" / "frontend_v2_handler.py",
            ROOT / "src" / "entrypoints" / "http" / "info_handler.py",
            ROOT / "src" / "entrypoints" / "http" / "people_snapshot_handler.py",
            ROOT / "src" / "entrypoints" / "http" / "task_attachment_read_handler.py",
            ROOT / "src" / "entrypoints" / "http" / "frontend_response_cache.py",
            ROOT / "src" / "entrypoints" / "http" / "group_query_handler.py",
        ]
        offenders = [str(path.relative_to(ROOT)) for path in removed_paths if path.exists()]
        self.assertEqual(offenders, [])

    def test_active_runtime_docs_do_not_point_to_old_canons_as_live_guidance(self) -> None:
        offenders: list[str] = []
        for file_path in _python_files([ROOT / "docs" / "architecture" / "runtime"]):
            content = file_path.read_text(encoding="utf-8")
            if "modular-monolith-v2.md" not in content:
                continue
            if "historical predecessor" in content or "historical" in content:
                continue
            offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_runtime_docs_do_not_use_wrapper_language_for_canonical_paths(self) -> None:
        offenders: list[str] = []
        target_files = [
            ROOT / "docs" / "architecture" / "overview.md",
            ROOT / "docs" / "architecture" / "entrypoints.md",
            ROOT / "docs" / "architecture" / "runtime-flow.md",
            ROOT / "docs" / "modules" / "attachments.md",
        ]
        forbidden_markers = ("transitional wrapper", "compatibility wrapper", "legacy wrapper")
        for file_path in target_files:
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_removed_technical_compatibility_roots_do_not_exist(self) -> None:
        removed_paths = [
            ROOT / "src" / "app",
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
            ROOT / "src" / "telegram",
            ROOT / "src" / "services" / "attachments",
            ROOT / "src" / "services" / "access",
            ROOT / "src" / "services" / "mappers",
            ROOT / "src" / "services" / "readmodels",
            ROOT / "src" / "services" / "render",
            ROOT / "src" / "services" / "notify",
            ROOT / "src" / "services" / "sync",
            ROOT / "src" / "services" / "usecases",
            ROOT / "src" / "services" / "sources",
            ROOT / "src" / "services",
            ROOT / "src" / "adapters",
            ROOT / "src" / "infra",
            ROOT / "src" / "observability",
            ROOT / "src" / "handlers",
            ROOT / "src" / "entrypoints_adapters",
        ]
        offenders: list[str] = []
        for path in removed_paths:
            if not path.exists():
                continue
            python_files = sorted(path.rglob("*.py"))
            if python_files:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_removed_top_level_historical_roots_do_not_exist_at_all(self) -> None:
        removed_paths = [
            ROOT / "src" / "jobs",
            ROOT / "src" / "render",
            ROOT / "src" / "notify",
            ROOT / "src" / "snapshot_engine",
            ROOT / "src" / "telegram",
            ROOT / "src" / "handlers",
            ROOT / "src" / "entrypoints_adapters",
        ]
        offenders = [str(path.relative_to(ROOT)) for path in removed_paths if path.exists()]
        self.assertEqual(offenders, [])

    def test_active_render_jobs_do_not_import_old_render_target_guard(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "jobs" / "render_timeline_job.py",
            ROOT / "src" / "jobs" / "render_designers_job.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "src.render.target_guard" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_paths_do_not_import_broad_snapshot_engine_surface(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "contexts" / "attachments",
            ROOT / "src" / "contexts" / "reminders",
            ROOT / "src" / "contexts" / "rendering",
            ROOT / "src" / "contexts" / "telegram_interaction",
            ROOT / "src" / "jobs",
            ROOT / "src" / "services" / "timer_pipeline.py",
            ROOT / "src" / "entrypoints" / "runtime" / "planner_runtime_entry.py",
            ROOT / "src" / "entrypoints" / "http" / "admin_queue_handler.py",
            ROOT / "src" / "entrypoints" / "http" / "admin_task_attachments_handler.py",
        ]
        for file_path in _python_files(target_paths):
            content = file_path.read_text(encoding="utf-8")
            if "get_snapshot_engine" in content and "src.contexts.snapshot.public" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
                continue
            if "get_attachment_snapshot_engine" in content:
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_runtime_paths_do_not_import_removed_services_layer(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "commands",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoint",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "infra",
            ROOT / "src" / "platform",
            ROOT / "src" / "worker",
            ROOT / "tests",
        ]
        forbidden_markers = (
            "src.services.errors",
            "src.services.timer_pipeline",
            "src.services.sources",
            "src.services.usecases",
            "src.adapters.store_ydb",
            "src.adapters.google_sheets",
        )
        for file_path in _python_files(target_paths):
            if file_path == Path(__file__).resolve():
                continue
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_active_runtime_paths_do_not_import_loose_adapter_roots(self) -> None:
        offenders: list[str] = []
        target_paths = [
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
            ROOT / "tests",
        ]
        forbidden_markers = (
            "src.adapters.telegram",
            "src.adapters.llm_google",
            "src.adapters.llm_openai",
            "src.adapters.llm_yandex",
        )
        for file_path in _python_files(target_paths):
            if file_path == Path(__file__).resolve():
                continue
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_reminders_public_surface_stays_small_and_delivery_owned(self) -> None:
        file_path = ROOT / "src" / "contexts" / "reminders" / "public.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("def get_delivery_api(", content)
        self.assertIn("def get_command_handlers(", content)
        for removed_helper in (
            "def get_public_api(",
            "def get_snapshot_read_api(",
            "def get_usecase(",
            "def get_formatter(",
            "def get_sender(",
            "def get_enhancer(",
            "def get_today_in_runtime_timezone(",
            "def get_job_runner(",
            "def make_reminder_request(",
        ):
            self.assertNotIn(removed_helper, content)

    def test_rendering_public_surface_stays_small_and_execution_owned(self) -> None:
        file_path = ROOT / "src" / "contexts" / "rendering" / "public.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("def get_execution_api(", content)
        self.assertIn("def get_command_handlers(", content)
        for removed_helper in (
            "def get_public_api(",
            "def get_snapshot_read_api(",
            "def get_timeline_usecase(",
            "def get_designers_usecase(",
            "def get_window(",
            "def get_request(",
            "def get_writer(",
            "def get_render_job(",
        ):
            self.assertNotIn(removed_helper, content)

    def test_telegram_public_surface_stays_small_and_interaction_owned(self) -> None:
        file_path = ROOT / "src" / "contexts" / "telegram_interaction" / "public.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("def get_interaction_api(", content)
        self.assertIn("def get_webhook_handler(", content)
        self.assertIn("def get_command_handlers(", content)
        for removed_helper in (
            "def get_public_api(",
            "def get_update_parser(",
            "def get_command_router(",
            "def get_snapshot_read_api(",
            "def get_usecase(",
            "def get_group_query_formatter(",
            "def get_sender(",
            "def make_group_query_request(",
            "def get_group_query_reply_job(",
        ):
            self.assertNotIn(removed_helper, content)

    def test_snapshot_public_surface_uses_canonical_api_names(self) -> None:
        file_path = ROOT / "src" / "contexts" / "snapshot" / "public.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("get_read_api", content)
        self.assertIn("get_attachment_api", content)
        self.assertIn("get_query_api", content)
        self.assertIn("get_update_api", content)
        for removed_helper in (
            "def get_public_api(",
            "def get_read_capability(",
            "def get_attachment_capability(",
            "def get_query_capability(",
            "def get_update_capability(",
        ):
            self.assertNotIn(removed_helper, content)

    def test_attachments_public_surface_stays_small_and_api_owned(self) -> None:
        file_path = ROOT / "src" / "contexts" / "attachments" / "public.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("def get_attachment_api(", content)
        self.assertIn("def get_supported_attachment_mime_types(", content)
        self.assertIn("def get_command_handlers(", content)
        for removed_helper in (
            "def get_public_api(",
            "def get_attachment_storage(",
            "def get_attachment_metadata_store(",
            "def get_attachment_finalize_service(",
            "def get_attachment_read_resolver(",
            "def get_doc_preview_converter(",
            "def get_attachment_snapshot_api(",
            "def get_attachment_command_flow(",
        ):
            self.assertNotIn(removed_helper, content)

    def test_operational_info_read_api_stays_thin_and_service_owned(self) -> None:
        file_path = ROOT / "src" / "contexts" / "access_api" / "internal" / "operational_info_read_api.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("OperationalInfoReadService", content)
        self.assertNotIn("def _summary_payload(", content)
        self.assertNotIn("def _detail_payload(", content)


if __name__ == "__main__":
    unittest.main()


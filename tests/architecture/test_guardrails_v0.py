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

    def test_app_bootstrap_does_not_build_attachment_converter_directly(self) -> None:
        file_path = ROOT / "src" / "app" / "bootstrap.py"
        content = file_path.read_text(encoding="utf-8")
        self.assertNotIn("from src.infra.doc_preview_converter import DocPreviewConverter", content)
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
            "tests/jobs",
            "tests/snapshot_engine",
            "tests/notify",
            "tests/render",
            "tests/telegram",
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
            ROOT / "docs" / "architecture" / "runtime" / "module-map.md",
            ROOT / "docs" / "architecture" / "runtime" / "entrypoints.md",
            ROOT / "docs" / "architecture" / "runtime" / "command-runtime.md",
            ROOT / "docs" / "integrations" / "attachments" / "backend-flow.md",
        ]
        forbidden_markers = ("transitional wrapper", "compatibility wrapper", "legacy wrapper")
        for file_path in target_files:
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_removed_technical_compatibility_roots_do_not_exist(self) -> None:
        removed_paths = [
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
        )
        for file_path in _python_files(target_paths):
            if file_path == Path(__file__).resolve():
                continue
            content = file_path.read_text(encoding="utf-8")
            if any(marker in content for marker in forbidden_markers):
                offenders.append(str(file_path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import ast
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_TARGETS = [
    ROOT / "index.py",
    ROOT / "local_run.py",
    ROOT / "src" / "entrypoints",
    ROOT / "src" / "jobs",
    ROOT / "src" / "worker",
]
FORBIDDEN_IMPORT_PREFIXES = (
    "src.legacy",
    "src.adapters.store_ydb",
    "src.entrypoints.jobs.legacy_store_write_job",
    "src.entrypoints.jobs.planner_pipeline_job",
    "src.entrypoints.jobs.planner_setup_job",
    "src.entrypoints.jobs.source_switch_job",
    "src.services.usecases.planner_runtime",
    "src.app.planner_bootstrap",
    "src.services.planner_runtime",
    "src.services.calendar_runtime",
    "src.services.render.task_table_runtime",
    "src.entrypoints.jobs.readmodel_probe_job",
    "src.entrypoints.jobs.readmodel_freshness",
    "src.services.usecases.planner_runtime",
    "core.bootstrap",
    "core.manager",
    "main",
)
INDEX_ALLOWED_IMPORTS = {
    "src.entrypoint.handler.handle",
    "src.platform.bootstrap.APP_TRIGGERS",
    "src.platform.bootstrap.get_app_context",
    "src.platform.bootstrap.get_dispatcher",
}


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for target in ACTIVE_TARGETS:
        if target.is_file():
            files.append(target)
            continue
        if target.is_dir():
            files.extend(sorted(target.rglob("*.py")))
    return files


def _full_import_name(node: ast.AST) -> list[str]:
    names: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            names.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            names.append(f"{module}.{alias.name}" if module else alias.name)
    return names


def main() -> int:
    violations: list[str] = []
    for file_path in _iter_python_files():
        tree = ast.parse(file_path.read_text(encoding="utf-8-sig"), filename=str(file_path))
        import_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in _full_import_name(node):
                    import_names.append(name)
                    for forbidden in FORBIDDEN_IMPORT_PREFIXES:
                        if name == forbidden or name.startswith(f"{forbidden}."):
                            violations.append(f"{file_path.relative_to(ROOT)} imports forbidden {name}")
        if file_path == ROOT / "index.py":
            unexpected = sorted(name for name in import_names if name not in INDEX_ALLOWED_IMPORTS)
            if unexpected:
                violations.append(
                    "index.py has unexpected imports: " + ", ".join(unexpected)
                )
    if violations:
        print("legacy_entrypoint_imports_check=failed")
        for violation in violations:
            print(violation)
        return 1
    print("legacy_entrypoint_imports_check=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

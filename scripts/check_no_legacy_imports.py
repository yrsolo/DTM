"""Guardrails to keep new runtime contours free from legacy imports."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    ("import core", [ROOT / "src" / "snapshot_engine", ROOT / "src" / "notify", ROOT / "src" / "render", ROOT / "src" / "entrypoints"]),
    ("from core", [ROOT / "src" / "snapshot_engine", ROOT / "src" / "notify", ROOT / "src" / "render", ROOT / "src" / "entrypoints"]),
    ("import pandas", [ROOT / "src" / "snapshot_engine", ROOT / "src" / "notify", ROOT / "src" / "render", ROOT / "src" / "entrypoints"]),
    ("GoogleSheetPlanner", [ROOT / "src" / "snapshot_engine", ROOT / "src" / "notify", ROOT / "src" / "render", ROOT / "src" / "entrypoints"]),
    ("build_planner_dependencies", [ROOT / "src" / "snapshot_engine", ROOT / "src" / "notify", ROOT / "src" / "render", ROOT / "src" / "entrypoints"]),
]

# Current known exceptions while migration is in progress.
EXCLUDE_SUBSTRINGS = {
    "src/entrypoints/http/group_query_handler.py",
    "src/entrypoints/http/group_query_tasks_loader.py",
    "src/entrypoints/jobs/planner_setup_job.py",
    "src/entrypoints/runtime/planner_runtime_entry.py",
}


def iter_py_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(item for item in path.rglob("*.py") if item.is_file()))
    return files


def is_excluded(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return any(marker in rel for marker in EXCLUDE_SUBSTRINGS)


def main() -> int:
    violations: list[str] = []
    for needle, scope in CHECKS:
        for file_path in iter_py_files(scope):
            if is_excluded(file_path):
                continue
            text = file_path.read_text(encoding="utf-8")
            if needle in text:
                rel = str(file_path.relative_to(ROOT)).replace("\\", "/")
                violations.append(f"{rel}: forbidden `{needle}`")

    if violations:
        print("check_no_legacy_imports: FAIL")
        for item in violations:
            print(f" - {item}")
        return 1

    print("check_no_legacy_imports: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

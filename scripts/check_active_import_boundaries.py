"""Guardrail checks for active import boundaries."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    (
        "import core",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "from core",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "src.services",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "src.adapters",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "src.legacy",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "src.snapshot_engine",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
    (
        "src.jobs",
        [
            ROOT / "index.py",
            ROOT / "local_run.py",
            ROOT / "src" / "contexts",
            ROOT / "src" / "entrypoints",
            ROOT / "src" / "platform",
        ],
    ),
]


def iter_py_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(item for item in path.rglob("*.py") if item.is_file()))
    return files


def main() -> int:
    violations: list[str] = []
    for needle, scope in CHECKS:
        for file_path in iter_py_files(scope):
            text = file_path.read_text(encoding="utf-8")
            if needle in text:
                rel = str(file_path.relative_to(ROOT)).replace("\\", "/")
                violations.append(f"{rel}: forbidden `{needle}`")

    if violations:
        print("check_active_import_boundaries: FAIL")
        for item in violations:
            print(f" - {item}")
        return 1

    print("check_active_import_boundaries: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

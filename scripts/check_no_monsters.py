"""Guardrail checks to prevent demonster regressions."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_RULES = [
    ("build_http_dispatch_handlers(", [ROOT / "index.py", ROOT / "src" / "entrypoints" / "http"]),
    ("HttpRouterContext", [ROOT / "index.py", ROOT / "src" / "entrypoints" / "http"]),
    ("GroupQueryHandlerContext", [ROOT / "index.py", ROOT / "src" / "entrypoints" / "http"]),
    ("RuntimeExecutionContext", [ROOT / "index.py", ROOT / "src" / "entrypoints" / "http"]),
    ("SyncReadmodelPipelineContext", [ROOT / "src" / "services", ROOT / "src" / "entrypoints"]),
]

LAMBDA_SCOPE = [
    ROOT / "index.py",
    ROOT / "src" / "entrypoints" / "http",
]


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.py") if p.is_file()))
    return files


def main() -> int:
    violations: list[str] = []

    for needle, scope in TEXT_RULES:
        for file_path in iter_files(scope):
            text = file_path.read_text(encoding="utf-8")
            if needle in text:
                violations.append(f"{file_path.relative_to(ROOT)}: forbidden symbol `{needle}`")

    lambda_pattern = re.compile(r"\blambda\b")
    for file_path in iter_files(LAMBDA_SCOPE):
        text = file_path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            if lambda_pattern.search(line):
                violations.append(f"{file_path.relative_to(ROOT)}:{idx}: lambda is forbidden in entrypoint wiring")

    if violations:
        print("check_no_monsters: FAIL")
        for item in violations:
            print(f" - {item}")
        return 1

    print("check_no_monsters: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

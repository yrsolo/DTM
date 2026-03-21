"""Export YC deploy defaults from config/deploy.yaml to GitHub Actions env/output files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def _load_yc_section(config_path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    section = raw.get("yandex_cloud", {})
    if not isinstance(section, dict):
        raise ValueError("deploy.yaml: 'yandex_cloud' section must be a mapping")
    return section


def _normalize(target: str, yc: dict[str, Any]) -> dict[str, str]:
    function_name_key = "function_name_test" if target == "test" else "function_name_prod"
    values = {
        "YC_FOLDER_ID": str(yc.get("folder_id", "")).strip(),
        "YC_SERVICE_ACCOUNT_ID": str(yc.get("service_account_id", "")).strip(),
        "YC_CLOUD_FUNCTION_NAME": str(yc.get(function_name_key, "")).strip(),
        "YC_FUNCTION_RUNTIME": str(yc.get("function_runtime", "python311")).strip(),
        "YC_FUNCTION_TIMEOUT": str(yc.get("function_timeout", "60s")).strip(),
        "YC_FUNCTION_MEMORY": str(yc.get("function_memory", "512Mb")).strip(),
        "YC_FUNCTION_ENTRYPOINT": str(yc.get("function_entrypoint", "index.handler")).strip(),
    }
    return values


def _validate_required_source(yc: dict[str, Any], target: str) -> None:
    function_name_key = "function_name_test" if target == "test" else "function_name_prod"
    required = (
        "folder_id",
        "service_account_id",
        function_name_key,
        "function_runtime",
        "function_timeout",
        "function_memory",
        "function_entrypoint",
    )
    missing = [key for key in required if not str(yc.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing required deploy values: {', '.join(missing)}")


def _append_key_values(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def _append_outputs(path: Path, values: dict[str, str]) -> None:
    outputs = {key.lower(): value for key, value in values.items()}
    with path.open("a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to deploy YAML config")
    parser.add_argument("--target", required=True, choices=("test", "prod"))
    parser.add_argument("--github-env", required=True, help="Path to GITHUB_ENV file")
    parser.add_argument("--github-output", required=True, help="Path to GITHUB_OUTPUT file")
    parser.add_argument("--strict", action="store_true", help="Fail when required fields are empty")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    github_env_path = Path(args.github_env)
    github_output_path = Path(args.github_output)

    yc = _load_yc_section(config_path)
    if args.strict:
        _validate_required_source(yc, args.target)
    values = _normalize(args.target, yc)

    _append_key_values(github_env_path, values)
    _append_outputs(github_output_path, values)

    print(
        "deploy_defaults"
        f" target={args.target}"
        f" function={values['YC_CLOUD_FUNCTION_NAME']}"
        f" runtime={values['YC_FUNCTION_RUNTIME']}"
        f" timeout={values['YC_FUNCTION_TIMEOUT']}"
        f" memory={values['YC_FUNCTION_MEMORY']}"
        f" entrypoint={values['YC_FUNCTION_ENTRYPOINT']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI failure surface
        print(f"export_deploy_defaults_error={exc}", file=sys.stderr)
        raise SystemExit(1)

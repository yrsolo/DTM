"""Sync .env keys into Yandex Lockbox secret payload."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def _clean_env_value(value: str) -> str:
    """Normalize env value by trimming whitespace and wrapping quotes."""
    return value.strip().strip('"').strip("'")


def _safe_print(text: str) -> None:
    """Print text safely on consoles with narrow encodings."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse key/value pairs from .env-like file."""
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = _clean_env_value(value)
        if key:
            result[key] = value
    return result


def _default_yc_binary() -> Path:
    """Return default local path to yc executable."""
    return Path.home() / "yandex-cloud" / "bin" / "yc.exe"


def parse_args() -> argparse.Namespace:
    """Parse CLI options for Lockbox sync."""
    parser = argparse.ArgumentParser(description="Sync local .env keys into Lockbox secret")
    parser.add_argument(
        "--secret-name",
        default="DTM",
        help="Target Lockbox secret name (default: DTM).",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to .env file (default: .env).",
    )
    parser.add_argument(
        "--google-key-file",
        type=Path,
        default=Path("key") / "google_key_poised-backbone-191400-4e9fc454915f.json",
        help="Path to Google service-account JSON file for GOOGLE_KEY_JSON payload entry.",
    )
    parser.add_argument(
        "--yc-binary",
        type=Path,
        default=_default_yc_binary(),
        help="Path to yc executable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload keys without creating new Lockbox version.",
    )
    return parser.parse_args()


def _build_payload_entries(env_map: dict[str, str], google_key_file: Path) -> list[dict[str, str]]:
    """Build Lockbox payload entries from env values and optional Google key JSON."""
    payload: list[dict[str, str]] = []
    for key, value in env_map.items():
        if value:
            payload.append({"key": key, "text_value": value})
    if google_key_file.exists():
        google_text = google_key_file.read_text(encoding="utf-8")
        payload = [item for item in payload if item["key"] != "GOOGLE_KEY_JSON"]
        payload.append({"key": "GOOGLE_KEY_JSON", "text_value": google_text})
    return payload


def _add_secret_version(yc_binary: Path, secret_name: str, payload: list[dict[str, str]]) -> None:
    """Publish new Lockbox secret version with prepared payload."""
    payload_json = json.dumps(payload, ensure_ascii=False)
    run = subprocess.run(
        [
            str(yc_binary),
            "lockbox",
            "secret",
            "add-version",
            "--name",
            secret_name,
            "--description",
            "sync from local env",
            "--payload",
            payload_json,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip() or "yc lockbox add-version failed")


def main() -> int:
    """Execute Lockbox sync flow in dry-run or live mode."""
    args = parse_args()
    env_map = _parse_env_file(args.env_file)
    payload = _build_payload_entries(env_map, args.google_key_file)
    payload_keys = sorted({entry["key"] for entry in payload})

    if args.dry_run:
        _safe_print(f"lockbox_sync_secret={args.secret_name}")
        _safe_print(f"lockbox_sync_keys_count={len(payload_keys)}")
        _safe_print(f"lockbox_sync_keys={','.join(payload_keys)}")
        return 0

    if not args.yc_binary.exists():
        raise FileNotFoundError(f"yc binary not found: {args.yc_binary}")

    _add_secret_version(args.yc_binary, args.secret_name, payload)
    _safe_print(f"lockbox_sync_secret={args.secret_name}")
    _safe_print(f"lockbox_sync_keys_count={len(payload_keys)}")
    _safe_print("lockbox_sync_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

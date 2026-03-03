"""Prepare manual production release inputs and Lockbox sync."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from sync_lockbox_from_env import _build_payload_entries, _default_yc_binary, _parse_env_file


REQUIRED_PROD_KEYS = (
    "TARGET_SHEET_NAME_PROD",
    "YC_CLOUD_FUNCTION_PROD_NAME",
    "YC_CLOUD_FUNCTION_PROD_ID",
    "WEB_DOMAIN",
    "API_DOMAIN_PROD",
    "API_DOMAIN_TEST",
    "STORE_MODE",
    "READMODEL_SOURCE",
    "NOTIFY_SOURCE",
    "RENDER_SOURCE",
    "YDB_ID_PROD",
    "YDB_ENDPOINT_PROD",
    "YDB_DATABASE_PROD",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare production release contour.")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to env file (default: .env).",
    )
    parser.add_argument(
        "--secret-name",
        default="DTM",
        help="Lockbox secret name (default: DTM).",
    )
    parser.add_argument(
        "--google-key-file",
        type=Path,
        default=Path("key") / "google_key_poised-backbone-191400-4e9fc454915f.json",
        help="Google key JSON file path.",
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
        help="Do not publish new Lockbox version; print checks only.",
    )
    return parser.parse_args()


def _validate_required_keys(env_map: dict[str, str]) -> list[str]:
    return [key for key in REQUIRED_PROD_KEYS if not env_map.get(key, "").strip()]


def _run_lockbox_sync(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "agent/sync_lockbox_from_env.py",
        "--secret-name",
        args.secret_name,
        "--env-file",
        str(args.env_file),
        "--google-key-file",
        str(args.google_key_file),
        "--yc-binary",
        str(args.yc_binary),
    ]
    for key in REQUIRED_PROD_KEYS:
        command.extend(["--require-key", key])
    if args.dry_run:
        command.append("--dry-run")

    run = subprocess.run(command, check=False)
    return run.returncode


def main() -> int:
    args = parse_args()
    env_map = _parse_env_file(args.env_file)
    missing = _validate_required_keys(env_map)
    if missing:
        print(f"missing_env_keys={','.join(missing)}")
        return 2

    payload_keys = sorted(
        {
            entry["key"]
            for entry in _build_payload_entries(
                env_map=env_map,
                google_key_file=args.google_key_file,
            )
        }
    )
    print(f"prod_release_env_ok={','.join(REQUIRED_PROD_KEYS)}")
    print(f"lockbox_payload_keys_count={len(payload_keys)}")

    rc = _run_lockbox_sync(args)
    if rc != 0:
        return rc

    print("next_step=run_manual_workflow_release_yc_function_prod")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_YC = Path.home() / "yandex-cloud" / "bin" / "yc.exe"
DEFAULT_DOMAIN = "dtm.solofarm.ru"
DEFAULT_CERTIFICATE_ID = "fpqsk82473vprlt5fv8p"
DEFAULT_SERVICE_ACCOUNT_ID = "aje1kqd422vq2vefkbbl"
DEFAULT_TEST_FUNCTION_ID = "d4e81vgi5vri8poe7qba"
DEFAULT_PROD_FUNCTION_ID = "d4e2qtl9l30ockjv2hn7"
DEFAULT_GATEWAY_NAME = "dtm-api-unified"
DEFAULT_TEST_PATH_PREFIX = "/test-front/{proxy+}"
DEFAULT_PROD_PATH_PREFIX = "/prod/{proxy+}"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "yc command failed")
    return completed


def _run_json(command: list[str]) -> dict | list:
    completed = _run(command)
    raw = completed.stdout.strip() or "{}"
    return json.loads(raw)


def _find_gateway_id(yc_binary: Path, name: str) -> str:
    payload = _run_json([str(yc_binary), "serverless", "api-gateway", "list", "--format", "json"])
    for item in payload if isinstance(payload, list) else []:
        if str(item.get("name", "")).strip() == name:
            return str(item.get("id", "")).strip()
    return ""


def _render_spec(
    *,
    test_function_id: str,
    prod_function_id: str,
    service_account_id: str,
    test_path_prefix: str,
    prod_path_prefix: str,
) -> str:
    return f"""openapi: 3.0.0
info:
  title: DTM Unified API
  version: 1.0.0
paths:
  {test_path_prefix}:
    x-yc-apigateway-any-method:
      parameters:
        - name: proxy
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {test_function_id}
        tag: $latest
        service_account_id: {service_account_id}
  {prod_path_prefix}:
    x-yc-apigateway-any-method:
      parameters:
        - name: proxy
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {prod_function_id}
        tag: $latest
        service_account_id: {service_account_id}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update unified API gateway for /test and /prod paths.")
    parser.add_argument("--yc-binary", type=Path, default=DEFAULT_YC)
    parser.add_argument("--gateway-name", default=DEFAULT_GATEWAY_NAME)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--certificate-id", default=DEFAULT_CERTIFICATE_ID)
    parser.add_argument("--service-account-id", default=DEFAULT_SERVICE_ACCOUNT_ID)
    parser.add_argument("--test-function-id", default=DEFAULT_TEST_FUNCTION_ID)
    parser.add_argument("--prod-function-id", default=DEFAULT_PROD_FUNCTION_ID)
    parser.add_argument("--test-path-prefix", default=DEFAULT_TEST_PATH_PREFIX)
    parser.add_argument("--prod-path-prefix", default=DEFAULT_PROD_PATH_PREFIX)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    if not args.yc_binary.exists():
        raise FileNotFoundError(f"yc binary not found: {args.yc_binary}")

    gateway_id = _find_gateway_id(args.yc_binary, args.gateway_name)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".openapi.yaml",
        prefix="dtm-unified-gateway-",
        delete=False,
    ) as tmp:
        tmp.write(
            _render_spec(
                test_function_id=args.test_function_id,
                prod_function_id=args.prod_function_id,
                service_account_id=args.service_account_id,
                test_path_prefix=args.test_path_prefix,
                prod_path_prefix=args.prod_path_prefix,
            )
        )
        spec_path = tmp.name

    if args.dry_run:
        print(f"gateway_name={args.gateway_name}")
        print(f"gateway_id={gateway_id or '<create-new>'}")
        print(f"domain={args.domain}")
        print(f"certificate_id={args.certificate_id}")
        print(f"spec_path={spec_path}")
        return 0

    if gateway_id:
        _run([str(args.yc_binary), "serverless", "api-gateway", "update", gateway_id, "--spec", spec_path])
        target_gateway_id = gateway_id
    else:
        _run([str(args.yc_binary), "serverless", "api-gateway", "create", args.gateway_name, "--spec", spec_path])
        target_gateway_id = _find_gateway_id(args.yc_binary, args.gateway_name)
        if not target_gateway_id:
            raise RuntimeError("unable to resolve gateway id after creation")

    try:
        _run(
            [
                str(args.yc_binary),
                "serverless",
                "api-gateway",
                "add-domain",
                target_gateway_id,
                "--domain",
                args.domain,
                "--certificate-id",
                args.certificate_id,
            ]
        )
    except RuntimeError as exc:
        if "already" not in str(exc).lower():
            raise

    print(f"gateway_id={target_gateway_id}")
    print(f"domain={args.domain}")
    print("unified_api_gateway_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

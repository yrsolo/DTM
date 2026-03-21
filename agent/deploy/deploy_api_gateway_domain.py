"""Deploy/update Yandex API Gateway and bind custom domain for test/prod contour."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv


def _env(name: str, default: str = "") -> str:
    import os

    return os.environ.get(name, default).strip()


def _default_yc_binary() -> Path:
    return Path.home() / "yandex-cloud" / "bin" / "yc.exe"


def _run_json(command: list[str]) -> dict:
    run = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip() or "yc command failed")
    raw = run.stdout.strip() or "{}"
    return json.loads(raw)


def _run(command: list[str]) -> None:
    run = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip() or "yc command failed")


def _resolve_function_id(yc_binary: Path, mode: str) -> str:
    env_id_key = "YC_CLOUD_FUNCTION_PROD_ID" if mode == "prod" else "YC_CLOUD_FUNCTION_ID"
    env_name_key = "YC_CLOUD_FUNCTION_PROD_NAME" if mode == "prod" else "YC_CLOUD_FUNCTION_NAME"
    function_id = _env(env_id_key)
    if function_id:
        return function_id

    function_name = _env(env_name_key)
    if not function_name:
        raise RuntimeError(
            f"Missing function identifier: set {env_id_key} or {env_name_key}."
        )
    payload = _run_json(
        [
            str(yc_binary),
            "serverless",
            "function",
            "get",
            "--name",
            function_name,
            "--format",
            "json",
        ]
    )
    resolved = str(payload.get("id", "")).strip()
    if not resolved:
        raise RuntimeError(f"Unable to resolve function id for name={function_name}")
    return resolved


def _render_spec(function_id: str, service_account_id: str) -> str:
    return (
        "openapi: 3.0.0\n"
        "info:\n"
        "  title: DTM API\n"
        "  version: 1.0.0\n"
        "paths:\n"
        "  /:\n"
        "    x-yc-apigateway-any-method:\n"
        "      x-yc-apigateway-integration:\n"
        "        type: cloud_functions\n"
        f"        function_id: {function_id}\n"
        "        tag: $latest\n"
        f"        service_account_id: {service_account_id}\n"
        "  /{proxy+}:\n"
        "    x-yc-apigateway-any-method:\n"
        "      parameters:\n"
        "        - name: proxy\n"
        "          in: path\n"
        "          required: true\n"
        "          schema:\n"
        "            type: string\n"
        "      x-yc-apigateway-integration:\n"
        "        type: cloud_functions\n"
        f"        function_id: {function_id}\n"
        "        tag: $latest\n"
        f"        service_account_id: {service_account_id}\n"
    )


def _find_gateway_id_by_name(yc_binary: Path, name: str) -> str:
    payload = _run_json(
        [str(yc_binary), "serverless", "api-gateway", "list", "--format", "json"]
    )
    for item in payload:
        if str(item.get("name", "")).strip() == name:
            return str(item.get("id", "")).strip()
    return ""


def _default_gateway_name(mode: str) -> str:
    env_key = "YC_API_GATEWAY_PROD_NAME" if mode == "prod" else "YC_API_GATEWAY_TEST_NAME"
    return _env(env_key) or f"dtm-api-{mode}"


def _default_gateway_id(mode: str) -> str:
    env_key = "YC_API_GATEWAY_PROD_ID" if mode == "prod" else "YC_API_GATEWAY_TEST_ID"
    return _env(env_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy/update API Gateway and attach custom domain."
    )
    parser.add_argument("--mode", choices=("test", "prod"), required=True)
    parser.add_argument("--gateway-name", default="", help="Gateway name override.")
    parser.add_argument("--gateway-id", default="", help="Gateway id override.")
    parser.add_argument("--domain", default="", help="Custom API domain override.")
    parser.add_argument(
        "--certificate-id",
        default="",
        help="Certificate id override for domain binding.",
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
        help="Print planned commands only.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    yc_binary = args.yc_binary
    if not yc_binary.exists():
        raise FileNotFoundError(f"yc binary not found: {yc_binary}")

    mode = args.mode
    gateway_name = args.gateway_name or _default_gateway_name(mode)
    domain = args.domain or _env("API_DOMAIN_PROD" if mode == "prod" else "API_DOMAIN_TEST")
    certificate_id = args.certificate_id or _env(
        "YC_API_CERTIFICATE_ID_PROD" if mode == "prod" else "YC_API_CERTIFICATE_ID_TEST"
    )
    service_account_id = _env("YC_RUNTIME_SERVICE_ACCOUNT_ID") or _env("YC_SERVICE_ACCOUNT_ID")
    if not domain:
        raise RuntimeError("Missing API domain. Set env or pass --domain.")
    if not certificate_id:
        raise RuntimeError("Missing certificate id. Set env or pass --certificate-id.")
    if not service_account_id:
        raise RuntimeError("Missing runtime service account id.")

    function_id = _resolve_function_id(yc_binary=yc_binary, mode=mode)
    gateway_id = args.gateway_id or _default_gateway_id(mode) or _find_gateway_id_by_name(
        yc_binary, gateway_name
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f".{mode}.openapi.yaml",
        prefix="dtm-api-gw-",
        delete=False,
        encoding="utf-8",
    ) as tmp_spec:
        tmp_spec.write(_render_spec(function_id=function_id, service_account_id=service_account_id))
        spec_path = tmp_spec.name

    if args.dry_run:
        print(f"mode={mode}")
        print(f"gateway_name={gateway_name}")
        print(f"gateway_id={gateway_id or '<create-new>'}")
        print(f"function_id={function_id}")
        print(f"domain={domain}")
        print(f"certificate_id={certificate_id}")
        print(f"spec_path={spec_path}")
        return 0

    if gateway_id:
        _run(
            [
                str(yc_binary),
                "serverless",
                "api-gateway",
                "update",
                gateway_id,
                "--spec",
                spec_path,
            ]
        )
        target_gateway_id = gateway_id
    else:
        _run(
            [
                str(yc_binary),
                "serverless",
                "api-gateway",
                "create",
                gateway_name,
                "--spec",
                spec_path,
            ]
        )
        target_gateway_id = _find_gateway_id_by_name(yc_binary, gateway_name)
        if not target_gateway_id:
            raise RuntimeError("Unable to resolve gateway id after creation.")

    try:
        _run(
            [
                str(yc_binary),
                "serverless",
                "api-gateway",
                "add-domain",
                target_gateway_id,
                "--domain",
                domain,
                "--certificate-id",
                certificate_id,
            ]
        )
    except RuntimeError as exc:
        message = str(exc).lower()
        if "already" not in message:
            raise

    print(f"api_gateway_mode={mode}")
    print(f"api_gateway_id={target_gateway_id}")
    print(f"api_domain={domain}")
    print(f"function_id={function_id}")
    print("api_gateway_domain_bind_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
DEFAULT_TEST_AUTH_FUNCTION_ID = "d4ebtgp4dhnbu1476gfu"
DEFAULT_PROD_AUTH_FUNCTION_ID = "d4ecpcsedh5k7l81d3lp"
DEFAULT_GATEWAY_NAME = "dtm-api-unified"
DEFAULT_FRONTEND_BASE_URL = "https://dtm-front.website.yandexcloud.net"
DEFAULT_GRAFANA_UPSTREAM = "http://89.169.132.198:3000"


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
    test_auth_function_id: str,
    prod_auth_function_id: str,
    service_account_id: str,
    frontend_base_url: str,
    grafana_upstream: str,
) -> str:
    frontend_base_url = frontend_base_url.rstrip("/")
    grafana_upstream = grafana_upstream.rstrip("/")
    return f"""openapi: 3.0.0
info:
  title: DTM Unified API
  version: 1.0.0
servers:
  - url: https://d5d84fgjajg4k61vh53h.8wihnuyr.apigw.yandexcloud.net
  - url: https://{DEFAULT_DOMAIN}
paths:
  /test/api/{{proxy+}}:
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

  /test/info:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {test_function_id}
        tag: $latest
        service_account_id: {service_account_id}

  /test/auth/{{proxy+}}:
    x-yc-apigateway-any-method:
      parameters:
        - name: proxy
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {test_auth_function_id}
        tag: $latest
        service_account_id: {service_account_id}

  /api/{{proxy+}}:
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

  /info:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {prod_function_id}
        tag: $latest
        service_account_id: {service_account_id}

  /auth/{{proxy+}}:
    x-yc-apigateway-any-method:
      parameters:
        - name: proxy
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: {prod_auth_function_id}
        tag: $latest
        service_account_id: {service_account_id}

  /grafana:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: http
        url: {grafana_upstream}/grafana/
        headers:
          Host: {DEFAULT_DOMAIN}
          X-Forwarded-Proto: https
          '*': '*'
        query:
          '*': '*'
        timeouts:
          connect: 1
          read: 30

  /grafana/:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: http
        url: {grafana_upstream}/grafana/
        headers:
          Host: {DEFAULT_DOMAIN}
          X-Forwarded-Proto: https
          '*': '*'
        query:
          '*': '*'
        timeouts:
          connect: 1
          read: 30

  /grafana/{{path+}}:
    x-yc-apigateway-any-method:
      parameters:
        - name: path
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: http
        url: {grafana_upstream}/grafana/{{path}}
        headers:
          Host: {DEFAULT_DOMAIN}
          X-Forwarded-Proto: https
          '*': '*'
        query:
          '*': '*'
        timeouts:
          connect: 1
          read: 30

  /test:
    get:
      x-yc-apigateway-integration:
        type: http
        url: {frontend_base_url}/test/index.html

  /test/:
    get:
      x-yc-apigateway-integration:
        type: http
        url: {frontend_base_url}/test/index.html

  /test/{{path+}}:
    x-yc-apigateway-any-method:
      parameters:
        - name: path
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: http
        url: {frontend_base_url}/test/{{path}}
        headers:
          '*': '*'
        query:
          '*': '*'

  /:
    get:
      x-yc-apigateway-integration:
        type: http
        url: {frontend_base_url}/

  /{{path+}}:
    x-yc-apigateway-any-method:
      parameters:
        - name: path
          in: path
          required: true
          schema:
            type: string
      x-yc-apigateway-integration:
        type: http
        url: {frontend_base_url}/{{path}}
        headers:
          '*': '*'
        query:
          '*': '*'
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update unified API gateway for canonical prod/test ingress.")
    parser.add_argument("--yc-binary", type=Path, default=DEFAULT_YC)
    parser.add_argument("--gateway-name", default=DEFAULT_GATEWAY_NAME)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--certificate-id", default=DEFAULT_CERTIFICATE_ID)
    parser.add_argument("--service-account-id", default=DEFAULT_SERVICE_ACCOUNT_ID)
    parser.add_argument("--test-function-id", default=DEFAULT_TEST_FUNCTION_ID)
    parser.add_argument("--prod-function-id", default=DEFAULT_PROD_FUNCTION_ID)
    parser.add_argument("--test-auth-function-id", default=DEFAULT_TEST_AUTH_FUNCTION_ID)
    parser.add_argument("--prod-auth-function-id", default=DEFAULT_PROD_AUTH_FUNCTION_ID)
    parser.add_argument("--frontend-base-url", default=DEFAULT_FRONTEND_BASE_URL)
    parser.add_argument("--grafana-upstream", default=DEFAULT_GRAFANA_UPSTREAM)
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
                test_auth_function_id=args.test_auth_function_id,
                prod_auth_function_id=args.prod_auth_function_id,
                service_account_id=args.service_account_id,
                frontend_base_url=args.frontend_base_url,
                grafana_upstream=args.grafana_upstream,
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

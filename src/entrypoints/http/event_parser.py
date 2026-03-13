"""HTTP event parsing helpers extracted from index entrypoint."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlparse


def extract_payload(event: Any) -> tuple[dict[str, Any], bool]:
    """Extract request payload and detect HTTP-like events."""

    if not isinstance(event, dict):
        return {}, False
    is_http = any(
        key in event
        for key in (
            "httpMethod",
            "method",
            "requestMethod",
            "path",
            "rawPath",
            "raw_path",
            "requestContext",
            "queryStringParameters",
            "rawQueryString",
            "params",
            "url",
        )
    )
    if "body" not in event:
        return event, is_http

    raw_body = event.get("body")
    if isinstance(raw_body, dict):
        return raw_body, True
    if isinstance(raw_body, str) and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass
    return {}, True


def normalize_path(path: str) -> str:
    """Normalize HTTP path for route matching."""

    text = str(path or "").strip()
    if not text:
        return ""
    if text.startswith(("http://", "https://")):
        parsed = urlparse(text)
        text = parsed.path or "/"
    text = text.replace("\\", "/")
    if "?" in text:
        text = text.split("?", 1)[0]
    while "//" in text:
        text = text.replace("//", "/")
    if not text.startswith("/"):
        text = f"/{text}"
    if len(text) > 1 and text.endswith("/"):
        text = text.rstrip("/")
    return text


def http_path(event: dict[str, Any]) -> str:
    """Resolve request path from different API Gateway event shapes."""

    def _normalize_proxy_path(value: Any) -> str:
        raw = str(value or "").strip()
        if not raw:
            return ""
        if raw == "/{proxy+}" or raw == "{proxy+}":
            return ""
        return raw if raw.startswith("/") else f"/{raw}"

    if not isinstance(event, dict):
        return ""
    # Proxy placeholders often carry the real route in pathParams/params.proxy.
    path_params = event.get("pathParams")
    if isinstance(path_params, dict):
        proxy = _normalize_proxy_path(path_params.get("proxy"))
        if proxy:
            return proxy
    params = event.get("params")
    if isinstance(params, dict):
        proxy = _normalize_proxy_path(params.get("proxy"))
        if proxy:
            return proxy
        params_path = _normalize_proxy_path(params.get("path"))
        if params_path:
            return params_path
        path_map = params.get("path")
        if isinstance(path_map, dict):
            for key in ("proxy", "path"):
                path = _normalize_proxy_path(path_map.get(key))
                if path:
                    return path

    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            path = _normalize_proxy_path(http_ctx.get("path"))
            if path:
                return path
            raw_path = _normalize_proxy_path(http_ctx.get("rawPath"))
            if raw_path:
                return raw_path
        rc_path = _normalize_proxy_path(request_context.get("path"))
        if rc_path:
            return rc_path
    for key in ("path", "rawPath", "raw_path", "url"):
        path = _normalize_proxy_path(event.get(key))
        if path:
            return path
    return ""


def http_method(event: dict[str, Any]) -> str:
    """Resolve HTTP method from API Gateway event."""

    if not isinstance(event, dict):
        return ""
    request_context = event.get("requestContext")
    if isinstance(request_context, dict):
        http_ctx = request_context.get("http")
        if isinstance(http_ctx, dict):
            method = str(http_ctx.get("method", "")).strip().upper()
            if method:
                return method
        method = str(request_context.get("httpMethod", "")).strip().upper()
        if method:
            return method
    for key in ("httpMethod", "method", "requestMethod"):
        method = str(event.get(key, "")).strip().upper()
        if method:
            return method
    return ""


def query_params(event: dict[str, Any]) -> dict[str, Any]:
    """Resolve and flatten query parameters from API Gateway event."""

    def _flatten(source: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in source.items():
            if isinstance(value, list):
                result[key] = str(value[0]).strip() if value else ""
            elif value is None:
                result[key] = ""
            else:
                result[key] = str(value).strip()
        return result

    if not isinstance(event, dict):
        return {}
    direct = event.get("queryStringParameters")
    if isinstance(direct, dict) and direct:
        return _flatten(direct)
    raw_query = event.get("rawQueryString")
    if isinstance(raw_query, str) and raw_query.strip():
        parsed = {key: value for key, value in parse_qsl(raw_query, keep_blank_values=True)}
        if parsed:
            return parsed
    multi = event.get("multiValueQueryStringParameters")
    if isinstance(multi, dict) and multi:
        return _flatten(multi)
    url = event.get("url")
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        parsed_url = urlparse(url)
        parsed = {key: value for key, value in parse_qsl(parsed_url.query, keep_blank_values=True)}
        if parsed:
            return parsed
    params = event.get("params")
    if isinstance(params, dict):
        qs = params.get("queryString")
        if isinstance(qs, dict):
            flattened = _flatten(qs)
            if flattened:
                return flattened
    multi_params = event.get("multiValueParams")
    if isinstance(multi_params, dict):
        qs = multi_params.get("queryString")
        if isinstance(qs, dict):
            flattened = _flatten(qs)
            if flattened:
                return flattened
    return {}


def header_params(event: dict[str, Any]) -> dict[str, Any]:
    """Resolve headers from different API Gateway event shapes."""

    def _flatten(source: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in source.items():
            if not str(key or "").strip():
                continue
            if isinstance(value, list):
                result[str(key)] = str(value[0]).strip() if value else ""
            elif value is None:
                result[str(key)] = ""
            else:
                result[str(key)] = str(value).strip()
        return result

    if not isinstance(event, dict):
        return {}

    merged: dict[str, Any] = {}

    params = event.get("params")
    if isinstance(params, dict):
        for key in ("header", "headers"):
            source = params.get(key)
            if isinstance(source, dict):
                merged.update(_flatten(source))

    multi_params = event.get("multiValueParams")
    if isinstance(multi_params, dict):
        for key in ("header", "headers"):
            source = multi_params.get(key)
            if isinstance(source, dict):
                merged.update(_flatten(source))

    direct = event.get("multiValueHeaders")
    if isinstance(direct, dict):
        merged.update(_flatten(direct))

    direct = event.get("headers")
    if isinstance(direct, dict):
        merged.update(_flatten(direct))

    return merged

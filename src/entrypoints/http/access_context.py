"""Browser-facing access boundary for trusted ingress and masking mode."""

from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest


def _header_map(headers: dict[str, object] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in dict(headers or {}).items():
        lowered = str(key or "").strip().lower()
        if not lowered:
            continue
        result[lowered] = str(value or "").strip()
    return result


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class AccessContext:
    mode: str
    trusted_ingress: bool
    authenticated: bool
    contour: str
    user_id: str | None
    user_role: str | None
    user_status: str | None
    fallback_reason: str | None = None

    @property
    def masked(self) -> bool:
        return self.mode == "masked"


def resolve_access_context(ctx: AppContext, req: HttpRequest) -> AccessContext:
    headers = _header_map(req.headers)
    api_cfg = dict(getattr(ctx.cfg.runtime, "api", {}) or {})
    fallback_mode = str(api_cfg.get("auth_trusted_fallback", "masked") or "masked").strip().lower() or "masked"
    expected_secret_header = str(
        api_cfg.get("auth_trusted_secret_header", "X-DTM-Proxy-Secret") or "X-DTM-Proxy-Secret"
    ).strip().lower()
    expected_secret = str(ctx.deps.get("browser_auth_proxy_secret") or "").strip()
    ingress_secret = headers.get(expected_secret_header, "")
    trusted_ingress = bool(expected_secret) and bool(ingress_secret) and compare_digest(ingress_secret, expected_secret)

    contour = str(headers.get("x-dtm-contour") or "").strip().lower()
    expected_contour = str(ctx.cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
    authenticated = _truthy(headers.get("x-dtm-authenticated", "0"))
    requested_mode = str(headers.get("x-dtm-access-mode") or "").strip().lower() or "masked"
    user_id = str(headers.get("x-dtm-user-id") or "").strip() or None
    user_role = str(headers.get("x-dtm-user-role") or "").strip() or None
    user_status = str(headers.get("x-dtm-user-status") or "").strip().lower() or None

    if fallback_mode != "masked":
        fallback_mode = "masked"

    if not trusted_ingress:
        return AccessContext(
            mode=fallback_mode,
            trusted_ingress=False,
            authenticated=False,
            contour=expected_contour,
            user_id=None,
            user_role=None,
            user_status=None,
            fallback_reason="untrusted_ingress",
        )
    enforce_contour = expected_contour in {"test", "prod"}
    if enforce_contour and contour and contour != expected_contour:
        return AccessContext(
            mode=fallback_mode,
            trusted_ingress=True,
            authenticated=False,
            contour=expected_contour,
            user_id=None,
            user_role=None,
            user_status=None,
            fallback_reason="contour_mismatch",
        )
    if authenticated and requested_mode == "full" and user_status == "approved":
        return AccessContext(
            mode="full",
            trusted_ingress=True,
            authenticated=True,
            contour=contour or expected_contour,
            user_id=user_id,
            user_role=user_role,
            user_status=user_status,
        )
    return AccessContext(
        mode="masked",
        trusted_ingress=True,
        authenticated=authenticated,
        contour=contour or expected_contour,
        user_id=user_id if authenticated else None,
        user_role=user_role if authenticated else None,
        user_status=user_status if authenticated else None,
        fallback_reason=None if requested_mode == "masked" else "policy_masked",
    )

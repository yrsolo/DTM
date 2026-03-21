"""Platform-level application error taxonomy for runtime boundaries."""

from __future__ import annotations


class AppError(Exception):
    """Base application error with machine-readable code."""

    def __init__(self, message: str, *, code: str = "app_error") -> None:
        super().__init__(message)
        self.code = code


class TransientError(AppError):
    """Retryable/transient failures (quota, timeouts, flaky integrations)."""

    def __init__(self, message: str, *, code: str = "transient_error") -> None:
        super().__init__(message, code=code)


class PermanentError(AppError):
    """Non-retryable failures (schema mismatch, invariant violations)."""

    def __init__(self, message: str, *, code: str = "permanent_error") -> None:
        super().__init__(message, code=code)


class UserError(AppError):
    """Input/user-triggered failures."""

    def __init__(self, message: str, *, code: str = "user_error") -> None:
        super().__init__(message, code=code)

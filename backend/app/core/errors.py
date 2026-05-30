"""Domain errors. Services raise these; ``main`` maps them to HTTP responses
with a consistent ``{"detail": ...}`` body."""
from __future__ import annotations


class AppError(Exception):
    """Base class for expected, client-facing errors."""

    status_code: int = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class BadRequestError(AppError):
    status_code = 400

"""Shared response envelopes."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    """Generic message envelope for simple acknowledgements."""

    detail: str


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    database: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    """Consistent error shape returned by the global exception handlers."""

    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Listing not found"}})

    detail: str

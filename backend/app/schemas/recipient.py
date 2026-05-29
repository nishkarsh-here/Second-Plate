"""Recipient schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RecipientType


class RecipientBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: RecipientType


class RecipientOut(RecipientBrief):
    lat: float
    lng: float
    capacity: int
    created_at: datetime

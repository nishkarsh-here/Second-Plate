"""Donor schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import DonorType


class DonorBrief(BaseModel):
    """Compact donor reference embedded in listings/predictions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: DonorType


class DonorOut(DonorBrief):
    lat: float
    lng: float
    address: str
    created_at: datetime

"""Pickup / claim schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recipient import RecipientBrief


class ClaimRequest(BaseModel):
    """Recipient claims a listing for pickup."""

    # Optional: when omitted, taken from the authenticated recipient's account.
    recipient_id: int | None = None
    scheduled_at: datetime | None = Field(
        default=None, description="Defaults to now if omitted"
    )


class PickupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    recipient_id: int
    scheduled_at: datetime
    completed_at: datetime | None
    servings_rescued: int
    recipient: RecipientBrief | None = None

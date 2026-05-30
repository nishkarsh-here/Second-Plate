"""Food-listing schemas (create / browse / detail) plus the urgency sub-object."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import FoodCategory, ListingStatus
from app.schemas.donor import DonorBrief


class UrgencyInfo(BaseModel):
    """Freshness-urgency descriptor surfaced as the green/amber/red badge."""

    score: float = Field(..., description="0..100, higher = more urgent")
    level: str = Field(..., description="fresh | soon | critical | expired")
    color: str = Field(..., description="green | amber | rose | slate")
    minutes_to_expiry: int
    label: str = Field(..., description="Human-readable, e.g. 'Expires in 42m'")


class ListingCreate(BaseModel):
    """Payload a donor submits to post a surplus listing."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "donor_id": 1,
                "food_type": "Vegetable biryani",
                "category": "cooked",
                "servings": 40,
                "prepared_at": "2026-05-30T12:30:00Z",
                "expires_at": "2026-05-30T18:30:00Z",
            }
        }
    )

    # Optional: when omitted, taken from the authenticated donor's account.
    donor_id: int | None = None
    food_type: str = Field(..., min_length=2, max_length=120)
    category: FoodCategory
    servings: int = Field(..., gt=0, le=100000)
    prepared_at: datetime
    expires_at: datetime
    # Optional: defaults to the donor's location when omitted.
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def _check_window(self) -> "ListingCreate":
        if self.expires_at <= self.prepared_at:
            raise ValueError("expires_at must be after prepared_at")
        return self


class ListingOut(BaseModel):
    """A listing as shown in the browse feed / map."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    food_type: str
    category: FoodCategory
    servings: int
    prepared_at: datetime
    expires_at: datetime
    status: ListingStatus
    lat: float
    lng: float
    created_at: datetime
    donor: DonorBrief
    # Computed by the service layer:
    urgency: UrgencyInfo
    distance_km: float | None = None


class ListingDetail(ListingOut):
    """Detail view (currently identical; kept distinct for future expansion)."""

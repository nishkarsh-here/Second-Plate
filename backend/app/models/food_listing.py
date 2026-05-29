"""FoodListing: a single surplus-food offer posted by a donor."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.enums import FoodCategory, ListingStatus

if TYPE_CHECKING:
    from app.models.donor import Donor
    from app.models.pickup import Pickup


class FoodListing(Base):
    __tablename__ = "food_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    donor_id: Mapped[int] = mapped_column(
        ForeignKey("donors.id", ondelete="CASCADE"), nullable=False
    )
    food_type: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[FoodCategory] = mapped_column(
        SAEnum(FoodCategory, name="food_category", native_enum=False), nullable=False
    )
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    prepared_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        SAEnum(ListingStatus, name="listing_status", native_enum=False),
        default=ListingStatus.available,
        nullable=False,
    )
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, server_default=func.now(), nullable=False
    )

    donor: Mapped["Donor"] = relationship(back_populates="listings")
    pickup: Mapped["Pickup | None"] = relationship(
        back_populates="listing", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("servings > 0", name="ck_listing_servings_positive"),
        CheckConstraint("expires_at > prepared_at", name="ck_listing_expiry_after_prepared"),
        # Hot path: "available listings expiring soon" + per-donor lookups.
        Index("ix_listings_status_expires", "status", "expires_at"),
        Index("ix_listings_donor_status", "donor_id", "status"),
    )

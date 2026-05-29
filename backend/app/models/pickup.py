"""Pickup: a recipient's claim against a listing, completed on collection."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime

if TYPE_CHECKING:
    from app.models.food_listing import FoodListing
    from app.models.impact_log import ImpactLog
    from app.models.recipient import Recipient


class Pickup(Base):
    __tablename__ = "pickups"

    id: Mapped[int] = mapped_column(primary_key=True)
    # One pickup per listing -> unique FK.
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("food_listings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        UTCDateTime, server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    servings_rescued: Mapped[int] = mapped_column(Integer, nullable=False)

    listing: Mapped["FoodListing"] = relationship(back_populates="pickup")
    recipient: Mapped["Recipient"] = relationship(back_populates="pickups")
    impact: Mapped["ImpactLog | None"] = relationship(
        back_populates="pickup", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("servings_rescued > 0", name="ck_pickup_servings_positive"),
    )

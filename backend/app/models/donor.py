"""Donor: a source of surplus food (restaurant, canteen, hostel, event)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.enums import DonorType

if TYPE_CHECKING:
    from app.models.donation_history import DonationHistory
    from app.models.food_listing import FoodListing


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[DonorType] = mapped_column(
        SAEnum(DonorType, name="donor_type", native_enum=False),
        nullable=False,
        index=True,
    )
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, server_default=func.now(), nullable=False
    )

    listings: Mapped[list["FoodListing"]] = relationship(
        back_populates="donor", cascade="all, delete-orphan"
    )
    history: Mapped[list["DonationHistory"]] = relationship(
        back_populates="donor", cascade="all, delete-orphan"
    )

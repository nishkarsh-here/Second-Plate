"""DonationHistory: daily per-donor donation record that feeds the ML model.

This is the training substrate for the surplus forecaster: one row per donor
per day with the servings donated and the dominant category. The seeder embeds
day-of-week, seasonal and event signal here so the model has something real to
learn.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FoodCategory

if TYPE_CHECKING:
    from app.models.donor import Donor


class DonationHistory(Base):
    __tablename__ = "donation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    donor_id: Mapped[int] = mapped_column(
        ForeignKey("donors.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    servings_donated: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[FoodCategory] = mapped_column(
        SAEnum(FoodCategory, name="food_category", native_enum=False), nullable=False
    )

    donor: Mapped["Donor"] = relationship(back_populates="history")

    __table_args__ = (
        CheckConstraint("servings_donated >= 0", name="ck_history_servings_nonneg"),
        Index("ix_history_donor_date", "donor_id", "date"),
    )

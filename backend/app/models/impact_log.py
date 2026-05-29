"""ImpactLog: the environmental/social outcome of a completed pickup."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.pickup import Pickup


class ImpactLog(Base):
    __tablename__ = "impact_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    pickup_id: Mapped[int] = mapped_column(
        ForeignKey("pickups.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    kg_saved: Mapped[float] = mapped_column(Float, nullable=False)
    co2e_kg: Mapped[float] = mapped_column(Float, nullable=False)
    people_served: Mapped[int] = mapped_column(Integer, nullable=False)

    pickup: Mapped["Pickup"] = relationship(back_populates="impact")

    __table_args__ = (
        CheckConstraint("kg_saved >= 0", name="ck_impact_kg_nonneg"),
        CheckConstraint("co2e_kg >= 0", name="ck_impact_co2e_nonneg"),
        CheckConstraint("people_served >= 0", name="ck_impact_people_nonneg"),
    )

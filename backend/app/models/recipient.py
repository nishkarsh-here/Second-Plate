"""Recipient: an organisation that rescues surplus food (NGO, shelter, kitchen)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.enums import RecipientType

if TYPE_CHECKING:
    from app.models.pickup import Pickup


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[RecipientType] = mapped_column(
        SAEnum(RecipientType, name="recipient_type", native_enum=False),
        nullable=False,
        index=True,
    )
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, server_default=func.now(), nullable=False
    )

    pickups: Mapped[list["Pickup"]] = relationship(back_populates="recipient")

"""ORM models.

Importing every model here ensures they are all registered on
``Base.metadata`` (so ``create_all`` / Alembic see them) and that SQLAlchemy can
resolve the string-based ``relationship`` targets.
"""
from app.models.donation_history import DonationHistory
from app.models.donor import Donor
from app.models.enums import (
    DonorType,
    FoodCategory,
    ListingStatus,
    RecipientType,
)
from app.models.food_listing import FoodListing
from app.models.impact_log import ImpactLog
from app.models.pickup import Pickup
from app.models.recipient import Recipient

__all__ = [
    "DonationHistory",
    "Donor",
    "DonorType",
    "FoodCategory",
    "FoodListing",
    "ImpactLog",
    "ListingStatus",
    "Pickup",
    "Recipient",
    "RecipientType",
]

"""Enumerations used across models, schemas and the ML pipeline.

All inherit from ``str`` so they serialize cleanly to JSON and compare to
plain strings, while still giving us DB-level CHECK/native-enum constraints.
"""
from __future__ import annotations

import enum


class DonorType(str, enum.Enum):
    restaurant = "restaurant"
    canteen = "canteen"
    hostel = "hostel"
    event = "event"


class RecipientType(str, enum.Enum):
    ngo = "ngo"
    shelter = "shelter"
    community_kitchen = "community_kitchen"


class FoodCategory(str, enum.Enum):
    cooked = "cooked"
    bakery = "bakery"
    produce = "produce"
    packaged = "packaged"


class ListingStatus(str, enum.Enum):
    available = "available"
    claimed = "claimed"
    picked_up = "picked_up"
    expired = "expired"


class UserRole(str, enum.Enum):
    donor = "donor"
    recipient = "recipient"

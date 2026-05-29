"""Donor <-> recipient matching by proximity.

Used by the seeder to assign realistic pickups, and available to the API for
recipient suggestions. Pure function over already-loaded rows so it can be
reused without a DB session.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.geo import haversine_km


@dataclass
class Ranked:
    recipient_id: int
    distance_km: float


def rank_recipients(
    listing_lat: float,
    listing_lng: float,
    recipients: list[tuple[int, float, float]],
    limit: int | None = None,
) -> list[Ranked]:
    """Rank ``(id, lat, lng)`` recipients by distance to a listing location."""
    ranked = [
        Ranked(rid, round(haversine_km(listing_lat, listing_lng, rlat, rlng), 2))
        for rid, rlat, rlng in recipients
    ]
    ranked.sort(key=lambda r: r.distance_km)
    return ranked[:limit] if limit else ranked

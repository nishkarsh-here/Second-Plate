"""Unit tests for the pure service helpers."""
from __future__ import annotations

from datetime import timedelta

from app.core.time import utcnow
from app.models.enums import FoodCategory
from app.services.geo import haversine_km
from app.services.urgency import compute_urgency


def test_haversine_known_distance():
    # Bengaluru -> Chennai is ~290 km.
    d = haversine_km(12.9716, 77.5946, 13.0827, 80.2707)
    assert 270 < d < 310


def test_haversine_zero():
    assert haversine_km(12.97, 77.59, 12.97, 77.59) == 0.0


def test_urgency_fresh_for_far_expiry():
    u = compute_urgency(FoodCategory.packaged, 10, utcnow() + timedelta(days=2))
    assert u.color == "green"
    assert u.level == "fresh"


def test_urgency_critical_when_near_expiry():
    u = compute_urgency(FoodCategory.cooked, 60, utcnow() + timedelta(minutes=10))
    assert u.color == "rose"
    assert u.score >= 70


def test_urgency_expired_in_past():
    u = compute_urgency(FoodCategory.cooked, 10, utcnow() - timedelta(minutes=5))
    assert u.level == "expired"
    assert u.minutes_to_expiry <= 0


def test_urgency_score_monotonic_in_time():
    cat = FoodCategory.cooked
    near = compute_urgency(cat, 30, utcnow() + timedelta(minutes=30)).score
    far = compute_urgency(cat, 30, utcnow() + timedelta(hours=6)).score
    assert near > far

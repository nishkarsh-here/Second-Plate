"""Test fixtures: an isolated SQLite database per test with a tiny seeded
dataset, wired into the app via the get_db dependency override."""
from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (register models on Base.metadata)
from app.core.time import utcnow
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    Donor,
    DonorType,
    FoodCategory,
    FoodListing,
    ImpactLog,
    ListingStatus,
    Pickup,
    Recipient,
    RecipientType,
)


def _seed_minimal(db) -> None:
    donor = Donor(name="Test Diner", type=DonorType.restaurant, lat=12.97, lng=77.59, address="MG Rd")
    recipient = Recipient(name="Hope NGO", type=RecipientType.ngo, lat=12.98, lng=77.60, capacity=100)
    db.add_all([donor, recipient])
    db.flush()

    now = utcnow()
    # An available listing for browse/claim tests.
    db.add(
        FoodListing(
            donor_id=donor.id,
            food_type="Veg biryani",
            category=FoodCategory.cooked,
            servings=30,
            prepared_at=now - timedelta(hours=1),
            expires_at=now + timedelta(hours=3),
            status=ListingStatus.available,
            lat=12.97,
            lng=77.59,
        )
    )
    # A completed pickup (+impact) so impact summary has data.
    done = FoodListing(
        donor_id=donor.id,
        food_type="Dal & rice",
        category=FoodCategory.cooked,
        servings=20,
        prepared_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=2) + timedelta(hours=4),
        status=ListingStatus.picked_up,
        lat=12.97,
        lng=77.59,
    )
    db.add(done)
    db.flush()
    pickup = Pickup(
        listing_id=done.id,
        recipient_id=recipient.id,
        scheduled_at=now - timedelta(days=1, hours=1),
        completed_at=now - timedelta(days=1),
        servings_rescued=20,
    )
    db.add(pickup)
    db.flush()
    db.add(ImpactLog(pickup_id=pickup.id, kg_saved=9.0, co2e_kg=22.5, people_served=15))
    db.commit()


@pytest.fixture()
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    seed_db = TestingSession()
    _seed_minimal(seed_db)
    seed_db.close()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

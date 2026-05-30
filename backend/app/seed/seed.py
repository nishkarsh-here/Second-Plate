"""Synthetic data generator with *real* signal.

Produces donors, recipients, ~14 months of daily ``donation_history``, and
several hundred completed pickups (+ impact) plus a set of currently-live
listings for the browse/map demo.

The daily surplus for a donor is built from interpretable components so the ML
model has genuine structure to learn (not noise):

    servings = base[type, donor]
             * day_of_week_factor[type][weekday]
             * seasonal_factor(date)          # smooth annual + festival peak
             * (1 + annual_trend * elapsed)   # slow per-donor drift
             * holiday_factor(date)           # learnable festival surge
             * random_event * noise           # the irreducible part

``holiday_factor`` uses the SAME calendar as the feature pipeline, so weekend /
holiday / seasonal effects are recoverable by the GradientBoostingRegressor.

Run directly:  python -m app.seed.seed
"""
from __future__ import annotations

import math
import random
from datetime import date, datetime, time, timedelta, timezone

import numpy as np
from faker import Faker
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.ml.features import is_holiday
from app.models import (
    DonationHistory,
    Donor,
    DonorType,
    FoodCategory,
    FoodListing,
    ImpactLog,
    ListingStatus,
    Pickup,
    Recipient,
    RecipientType,
    User,
)
from app.services.impact_service import impact_for_servings
from app.services.matching import rank_recipients

# Roughly central Bengaluru; donors/recipients scatter ~5 km around it.
CITY_LAT, CITY_LNG = 12.9716, 77.5946
COORD_JITTER = 0.045

# Mon..Sun multipliers per donor type.
DOW_FACTOR: dict[str, list[float]] = {
    "restaurant": [0.90, 0.90, 0.95, 1.00, 1.25, 1.45, 1.30],
    "canteen": [1.20, 1.20, 1.20, 1.15, 1.05, 0.50, 0.40],
    "hostel": [1.05, 1.05, 1.00, 1.00, 1.00, 0.90, 0.85],
    "event": [0.60, 0.60, 0.65, 0.70, 1.00, 1.60, 1.40],
}

BASE_RANGE: dict[str, tuple[int, int]] = {
    "restaurant": (28, 55),
    "canteen": (45, 85),
    "hostel": (50, 90),
    "event": (20, 45),
}

# Category mix per donor type (weights).
CATEGORY_WEIGHTS: dict[str, dict[FoodCategory, float]] = {
    "restaurant": {FoodCategory.cooked: 0.78, FoodCategory.bakery: 0.12, FoodCategory.produce: 0.10},
    "canteen": {FoodCategory.cooked: 0.88, FoodCategory.packaged: 0.12},
    "hostel": {FoodCategory.cooked: 0.92, FoodCategory.produce: 0.08},
    "event": {FoodCategory.cooked: 0.45, FoodCategory.packaged: 0.40, FoodCategory.bakery: 0.15},
}

FOOD_NAMES: dict[FoodCategory, list[str]] = {
    FoodCategory.cooked: [
        "Vegetable biryani", "Dal & rice", "Mixed curry & roti", "Vegetable pulao",
        "Sambar rice", "Pasta primavera", "Fried rice", "Khichdi", "Rajma chawal",
        "Chole & bhature", "Paneer curry & naan",
    ],
    FoodCategory.bakery: [
        "Assorted bread", "Butter croissants", "Muffins", "Mixed pastries",
        "Dinner buns", "Cookies & rusks",
    ],
    FoodCategory.produce: [
        "Mixed vegetables", "Seasonal fruit", "Salad greens", "Tomatoes & onions",
        "Leafy greens crate",
    ],
    FoodCategory.packaged: [
        "Packaged meal boxes", "Snack packs", "Juice cartons", "Canned goods",
        "Milk packets", "Sealed sandwich packs",
    ],
}

DONOR_NAME_BITS: dict[str, tuple[list[str], list[str]]] = {
    "restaurant": (
        ["Spice", "Curry", "Saffron", "Tandoori", "Green", "Royal", "Urban", "Coastal"],
        ["Garden", "Leaf", "House", "Kitchen", "Bistro", "Table", "Diner"],
    ),
    "canteen": (
        ["TechPark", "Campus", "Central", "Riverside", "Metro", "City"],
        ["Canteen", "Cafeteria", "Mess", "Food Court"],
    ),
    "hostel": (
        ["Sunrise", "Maple", "Lakeview", "Hillside", "Comfort", "Student"],
        ["Hostel Mess", "Residency Kitchen", "PG Mess", "Hostel Dining"],
    ),
    "event": (
        ["Grand", "Crown", "Lotus", "Heritage", "Skyline", "Pearl"],
        ["Convention Centre", "Banquet Hall", "Events", "Pavilion", "Gardens"],
    ),
}

RECIPIENT_NAME_BITS: dict[str, tuple[list[str], list[str]]] = {
    "ngo": (["Helping", "Hope", "Seva", "Annadaan", "Karuna", "Uday"], ["Hands", "Foundation", "Trust", "Welfare", "Mission"]),
    "shelter": (["Shanti", "Aashray", "Safe", "Haven", "Refuge"], ["Shelter", "Home", "Sadan", "House"]),
    "community_kitchen": (["Community", "Langar", "Akshaya", "Daily Bread", "Open"], ["Kitchen", "Bhojanalaya", "Table", "Meals"]),
}


def _jitter_coord(rng: np.random.Generator, base: float) -> float:
    return round(base + float(rng.normal(0, COORD_JITTER)), 6)


def _seasonal_factor(d: date) -> float:
    # Peak around late October (festival season), trough in late winter.
    doy = d.timetuple().tm_yday
    return 1.0 + 0.15 * math.sin(2 * math.pi * (doy - 209) / 365.0)


def _holiday_factor(d: date, dtype: str, rng: np.random.Generator) -> float:
    factor = 1.0
    if is_holiday(d):
        factor *= float(rng.uniform(1.4, 2.2)) if dtype == "event" else float(rng.uniform(1.2, 1.6))
    # Unpredictable one-off local events -> irreducible noise (no feature for it).
    if rng.random() < (0.04 if dtype == "event" else 0.015):
        factor *= float(rng.uniform(1.5, 2.5))
    return factor


def _pick_name(bits: dict[str, tuple[list[str], list[str]]], key: str, used: set[str], rng: random.Random) -> str:
    prefixes, suffixes = bits[key]
    for _ in range(40):
        name = f"{rng.choice(prefixes)} {rng.choice(suffixes)}"
        if name not in used:
            used.add(name)
            return name
    name = f"{rng.choice(prefixes)} {rng.choice(suffixes)} {rng.randint(2, 99)}"
    used.add(name)
    return name


def _weighted_category(weights: dict[FoodCategory, float], rng: random.Random) -> FoodCategory:
    cats, probs = zip(*weights.items())
    return rng.choices(cats, weights=probs, k=1)[0]


def reset(db: Session) -> None:
    """Delete all rows in FK-safe order (idempotent re-seed)."""
    for model in (ImpactLog, Pickup, FoodListing, DonationHistory, User, Recipient, Donor):
        db.execute(delete(model))
    db.commit()


def refresh_live_listings(db: Session, random_state: int | None = None) -> int:
    """Regenerate the live (available/claimed) demo listings with fresh
    timestamps. Safe to run on every boot: leaves donors, recipients, historical
    pickups, impact and user accounts untouched, so the browse/map never go
    stale even though the database persists across deploys."""
    pyrng = random.Random(random_state)
    rng = np.random.default_rng(random_state)

    stale_ids = list(
        db.scalars(
            select(FoodListing.id).where(
                FoodListing.status.in_([ListingStatus.available, ListingStatus.claimed])
            )
        ).all()
    )
    if stale_ids:
        db.execute(delete(Pickup).where(Pickup.listing_id.in_(stale_ids)))
        db.execute(delete(FoodListing).where(FoodListing.id.in_(stale_ids)))
        db.commit()

    donors = list(db.scalars(select(Donor)).all())
    recipients = list(db.scalars(select(Recipient)).all())
    if not donors or not recipients:
        return 0
    recip_locs = [(r.id, r.lat, r.lng) for r in recipients]

    now = datetime.now(timezone.utc)
    claim_targets: list[FoodListing] = []
    created = 0
    for _ in range(58):
        donor = pyrng.choice(donors)
        lo, hi = BASE_RANGE[donor.type.value]
        category = _weighted_category(CATEGORY_WEIGHTS[donor.type.value], pyrng)
        servings = max(4, int(round(pyrng.uniform(lo, hi) * pyrng.uniform(0.3, 0.8))))
        if pyrng.random() < 0.35:
            expires = now + timedelta(minutes=pyrng.randint(20, 6 * 60))
        else:
            expires = now + timedelta(hours=pyrng.randint(8, 5 * 24))
        listing = FoodListing(
            donor_id=donor.id,
            food_type=pyrng.choice(FOOD_NAMES[category]),
            category=category,
            servings=servings,
            prepared_at=now - timedelta(minutes=pyrng.randint(20, 240)),
            expires_at=expires,
            status=ListingStatus.available,
            lat=_jitter_coord(rng, donor.lat),
            lng=_jitter_coord(rng, donor.lng),
        )
        db.add(listing)
        created += 1
        if pyrng.random() < 0.25:
            claim_targets.append(listing)
    db.flush()

    for listing in claim_targets:
        listing.status = ListingStatus.claimed
        nearby = rank_recipients(listing.lat, listing.lng, recip_locs, limit=3)
        db.add(
            Pickup(
                listing_id=listing.id,
                recipient_id=pyrng.choice(nearby).recipient_id,
                scheduled_at=now + timedelta(minutes=pyrng.randint(20, 90)),
                completed_at=None,
                servings_rescued=listing.servings,
            )
        )
    db.commit()
    return created


def seed(
    db: Session,
    *,
    n_donors: int = 40,
    n_recipients: int = 15,
    months: int = 14,
    recent_days: int = 120,
    random_state: int = 42,
    do_reset: bool = True,
) -> dict:
    rng = np.random.default_rng(random_state)
    pyrng = random.Random(random_state)
    fake = Faker()
    Faker.seed(random_state)

    if do_reset:
        reset(db)

    # --- Recipients ---
    recipients: list[Recipient] = []
    used_r: set[str] = set()
    rtypes = list(RecipientType)
    for i in range(n_recipients):
        rtype = rtypes[i % len(rtypes)]
        recipients.append(
            Recipient(
                name=_pick_name(RECIPIENT_NAME_BITS, rtype.value, used_r, pyrng),
                type=rtype,
                lat=_jitter_coord(rng, CITY_LAT),
                lng=_jitter_coord(rng, CITY_LNG),
                capacity=int(pyrng.choice([80, 120, 150, 200, 250, 300])),
            )
        )
    db.add_all(recipients)
    db.flush()
    recip_locs = [(r.id, r.lat, r.lng) for r in recipients]

    # --- Donors (+ per-donor latent parameters) ---
    donors: list[Donor] = []
    donor_params: dict[int, dict] = {}
    used_d: set[str] = set()
    dtypes = list(DonorType)
    for i in range(n_donors):
        dtype = dtypes[i % len(dtypes)]
        lat = _jitter_coord(rng, CITY_LAT)
        lng = _jitter_coord(rng, CITY_LNG)
        donor = Donor(
            name=_pick_name(DONOR_NAME_BITS, dtype.value, used_d, pyrng),
            type=dtype,
            lat=lat,
            lng=lng,
            address=fake.street_address() + ", Bengaluru",
        )
        donors.append(donor)
    db.add_all(donors)
    db.flush()

    for donor in donors:
        lo, hi = BASE_RANGE[donor.type.value]
        donor_params[donor.id] = {
            "type": donor.type.value,
            "base": float(rng.uniform(lo, hi)),
            "trend": float(rng.uniform(-0.12, 0.22)),
            "primary": _weighted_category(CATEGORY_WEIGHTS[donor.type.value], pyrng),
        }

    # --- Daily donation history (the ML training substrate) ---
    end_date = date.today()
    start_date = end_date - timedelta(days=int(months * 30.4))
    total_days = (end_date - start_date).days

    history_rows: list[dict] = []
    # Keep recent per-donor surplus to drive realistic pickups below.
    recent_surplus: dict[int, list[tuple[date, int, FoodCategory]]] = {d.id: [] for d in donors}

    for donor in donors:
        p = donor_params[donor.id]
        dow = DOW_FACTOR[p["type"]]
        for offset in range(total_days + 1):
            d = start_date + timedelta(days=offset)
            frac = offset / 365.0
            noise = float(np.clip(rng.normal(1.0, 0.10), 0.7, 1.4))
            value = (
                p["base"]
                * dow[d.weekday()]
                * _seasonal_factor(d)
                * (1 + p["trend"] * frac)
                * _holiday_factor(d, p["type"], rng)
                * noise
            )
            servings = max(0, int(round(value)))
            category = p["primary"] if pyrng.random() < 0.8 else _weighted_category(
                CATEGORY_WEIGHTS[p["type"]], pyrng
            )
            history_rows.append(
                {
                    "donor_id": donor.id,
                    "date": d,
                    "servings_donated": servings,
                    "category": category,
                }
            )
            if offset >= total_days - recent_days:
                recent_surplus[donor.id].append((d, servings, category))

    db.execute(insert(DonationHistory), history_rows)
    db.flush()

    # --- Completed pickups + impact over the recent window (feeds dashboards) ---
    listings: list[FoodListing] = []
    pickups: list[Pickup] = []
    impacts: list[ImpactLog] = []

    for donor in donors:
        for d, surplus, category in recent_surplus[donor.id]:
            if surplus <= 0 or pyrng.random() > 0.34:
                continue
            servings = max(3, int(round(surplus * pyrng.uniform(0.4, 0.9))))
            prep_hour = pyrng.randint(10, 15)
            prepared = datetime.combine(d, time(prep_hour, pyrng.randint(0, 59)), tzinfo=timezone.utc)
            expires = prepared + timedelta(hours=pyrng.randint(3, 8))

            listing = FoodListing(
                donor_id=donor.id,
                food_type=pyrng.choice(FOOD_NAMES[category]),
                category=category,
                servings=servings,
                prepared_at=prepared,
                expires_at=expires,
                status=ListingStatus.picked_up,
                lat=_jitter_coord(rng, donor.lat),
                lng=_jitter_coord(rng, donor.lng),
            )
            listings.append(listing)

    db.add_all(listings)
    db.flush()

    # Pair each completed listing with a nearby recipient + log its impact.
    for listing in listings:
        nearby = rank_recipients(listing.lat, listing.lng, recip_locs, limit=3)
        recipient_id = pyrng.choice(nearby).recipient_id
        scheduled = listing.prepared_at + timedelta(minutes=pyrng.randint(30, 120))
        completed = scheduled + timedelta(minutes=pyrng.randint(20, 90))
        pickup = Pickup(
            listing_id=listing.id,
            recipient_id=recipient_id,
            scheduled_at=scheduled,
            completed_at=completed,
            servings_rescued=listing.servings,
        )
        pickups.append(pickup)
    db.add_all(pickups)
    db.flush()

    for pickup in pickups:
        kg, co2e, people = impact_for_servings(pickup.servings_rescued)
        impacts.append(
            ImpactLog(pickup_id=pickup.id, kg_saved=kg, co2e_kg=co2e, people_served=people)
        )
    db.add_all(impacts)

    # --- Currently-live listings for the browse/map demo ---
    now = datetime.now(timezone.utc)
    live_available = 0
    live_claimed = 0
    claim_targets: list[FoodListing] = []

    for _ in range(58):
        donor = pyrng.choice(donors)
        p = donor_params[donor.id]
        category = p["primary"] if pyrng.random() < 0.7 else _weighted_category(
            CATEGORY_WEIGHTS[p["type"]], pyrng
        )
        servings = max(4, int(round(p["base"] * pyrng.uniform(0.3, 0.8))))
        # ~35% expire soon (amber/rose urgency); the rest last up to ~5 days so the
        # demo's browse/map stay populated for days after a single seed.
        if pyrng.random() < 0.35:
            expires = now + timedelta(minutes=pyrng.randint(20, 6 * 60))
        else:
            expires = now + timedelta(hours=pyrng.randint(8, 5 * 24))
        prepared = now - timedelta(minutes=pyrng.randint(20, 240))
        listing = FoodListing(
            donor_id=donor.id,
            food_type=pyrng.choice(FOOD_NAMES[category]),
            category=category,
            servings=servings,
            prepared_at=prepared,
            expires_at=expires,
            status=ListingStatus.available,
            lat=_jitter_coord(rng, donor.lat),
            lng=_jitter_coord(rng, donor.lng),
        )
        db.add(listing)
        live_available += 1
        if pyrng.random() < 0.25:
            claim_targets.append(listing)

    db.flush()

    # A handful of already-claimed (not yet completed) listings for "My Listings".
    for listing in claim_targets:
        listing.status = ListingStatus.claimed
        nearby = rank_recipients(listing.lat, listing.lng, recip_locs, limit=3)
        db.add(
            Pickup(
                listing_id=listing.id,
                recipient_id=pyrng.choice(nearby).recipient_id,
                scheduled_at=now + timedelta(minutes=pyrng.randint(20, 90)),
                completed_at=None,
                servings_rescued=listing.servings,
            )
        )
        live_available -= 1
        live_claimed += 1

    db.commit()

    summary = {
        "donors": len(donors),
        "recipients": len(recipients),
        "donation_history_rows": len(history_rows),
        "completed_pickups": len(pickups),
        "live_available_listings": live_available,
        "live_claimed_listings": live_claimed,
        "history_from": start_date.isoformat(),
        "history_to": end_date.isoformat(),
    }
    return summary


def main() -> None:
    import argparse

    from sqlalchemy import func, select

    parser = argparse.ArgumentParser(description="Seed SecondPlate with synthetic data.")
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="Skip seeding when donors already exist (safe to run on every boot).",
    )
    parser.add_argument(
        "--refresh-live",
        action="store_true",
        help="Only regenerate the live demo listings with fresh timestamps.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.refresh_live:
            count = refresh_live_listings(db)
            print(f"Refreshed live listings: {count}")
            return
        if args.if_empty:
            existing = db.scalar(select(func.count()).select_from(Donor)) or 0
            if existing:
                print(f"Seed skipped — {existing} donors already present.")
                return
        result = seed(db)
        print("Seed complete:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

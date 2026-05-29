"""Impact analytics via SQL aggregation.

Headline KPIs (meals, kg, CO2e, people) and trend breakdowns are computed with
GROUP BY / SUM against the completed pickups joined to their impact rows. A
dialect-aware day bucket keeps the time series portable across SQLite and
PostgreSQL.

Conversion factors (documented in the README):
  - 1 serving  ~= 0.45 kg of food rescued
  - 1 kg food  ~= 2.5 kg CO2e avoided (production + disposal footprint)
  - 1 serving  ~= 0.75 people served (some receive multiple servings)
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.models import Donor, FoodListing, ImpactLog, ListingStatus, Pickup, Recipient
from app.models.enums import FoodCategory
from app.schemas.impact import (
    CategoryBreakdown,
    ImpactSummary,
    StatDelta,
    TopDonor,
    TrendPoint,
    TrendsResponse,
)

KG_PER_SERVING = 0.45
CO2E_PER_KG = 2.5
PEOPLE_PER_SERVING = 0.75


def impact_for_servings(servings: int) -> tuple[float, float, int]:
    """Derive (kg_saved, co2e_kg, people_served) for a number of servings."""
    kg = round(servings * KG_PER_SERVING, 2)
    co2e = round(kg * CO2E_PER_KG, 2)
    people = max(1, round(servings * PEOPLE_PER_SERVING))
    return kg, co2e, people


def _delta_pct(current: float, previous: float) -> float | None:
    if not previous:
        return None
    return round((current - previous) / previous * 100, 1)


def _completed_agg(db: Session, lo: datetime, hi: datetime):
    """SUM servings/kg/co2e/people for pickups completed in [lo, hi)."""
    stmt = (
        select(
            func.coalesce(func.sum(Pickup.servings_rescued), 0),
            func.coalesce(func.sum(ImpactLog.kg_saved), 0.0),
            func.coalesce(func.sum(ImpactLog.co2e_kg), 0.0),
            func.coalesce(func.sum(ImpactLog.people_served), 0),
        )
        .select_from(Pickup)
        .join(ImpactLog, ImpactLog.pickup_id == Pickup.id)
        .where(
            Pickup.completed_at.is_not(None),
            Pickup.completed_at >= lo,
            Pickup.completed_at < hi,
        )
    )
    return db.execute(stmt).one()


def summary(db: Session, window_days: int = 30) -> ImpactSummary:
    now = utcnow()
    start = now - timedelta(days=window_days)
    prev_start = start - timedelta(days=window_days)

    cur = _completed_agg(db, start, now)
    prev = _completed_agg(db, prev_start, start)

    active = (
        db.scalar(
            select(func.count())
            .select_from(FoodListing)
            .where(
                FoodListing.status == ListingStatus.available,
                FoodListing.expires_at > now,
            )
        )
        or 0
    )
    total_donors = db.scalar(select(func.count()).select_from(Donor)) or 0
    total_recipients = db.scalar(select(func.count()).select_from(Recipient)) or 0

    return ImpactSummary(
        meals_rescued=StatDelta(value=float(cur[0]), delta_pct=_delta_pct(cur[0], prev[0])),
        kg_saved=StatDelta(value=round(float(cur[1]), 1), delta_pct=_delta_pct(cur[1], prev[1])),
        co2e_avoided_kg=StatDelta(
            value=round(float(cur[2]), 1), delta_pct=_delta_pct(cur[2], prev[2])
        ),
        people_served=StatDelta(value=float(cur[3]), delta_pct=_delta_pct(cur[3], prev[3])),
        active_listings=int(active),
        total_donors=int(total_donors),
        total_recipients=int(total_recipients),
        window_days=window_days,
    )


def _day_bucket():
    """Truncate completed_at to a day, portably across SQLite and PostgreSQL."""
    if settings.is_sqlite:
        return func.date(Pickup.completed_at)
    return cast(Pickup.completed_at, Date)


def _coerce_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def trends(db: Session, range_days: int = 30) -> TrendsResponse:
    now = utcnow()
    start = now - timedelta(days=range_days)
    day = _day_bucket()

    series_rows = db.execute(
        select(
            day.label("day"),
            func.coalesce(func.sum(Pickup.servings_rescued), 0),
            func.coalesce(func.sum(ImpactLog.kg_saved), 0.0),
        )
        .select_from(Pickup)
        .join(ImpactLog, ImpactLog.pickup_id == Pickup.id)
        .where(Pickup.completed_at.is_not(None), Pickup.completed_at >= start)
        .group_by(day)
        .order_by(day)
    ).all()
    series = [
        TrendPoint(date=_coerce_date(r[0]), meals=int(r[1]), kg_saved=round(float(r[2]), 1))
        for r in series_rows
    ]

    cat_rows = db.execute(
        select(
            FoodListing.category,
            func.coalesce(func.sum(Pickup.servings_rescued), 0),
            func.coalesce(func.sum(ImpactLog.kg_saved), 0.0),
        )
        .select_from(Pickup)
        .join(FoodListing, FoodListing.id == Pickup.listing_id)
        .join(ImpactLog, ImpactLog.pickup_id == Pickup.id)
        .where(Pickup.completed_at.is_not(None), Pickup.completed_at >= start)
        .group_by(FoodListing.category)
    ).all()
    by_category = sorted(
        [
            CategoryBreakdown(
                category=FoodCategory(r[0]), servings=int(r[1]), kg_saved=round(float(r[2]), 1)
            )
            for r in cat_rows
        ],
        key=lambda c: c.servings,
        reverse=True,
    )

    donor_rows = db.execute(
        select(
            Donor.id,
            Donor.name,
            Donor.type,
            func.coalesce(func.sum(Pickup.servings_rescued), 0),
            func.count(Pickup.id),
        )
        .select_from(Pickup)
        .join(FoodListing, FoodListing.id == Pickup.listing_id)
        .join(Donor, Donor.id == FoodListing.donor_id)
        .where(Pickup.completed_at.is_not(None), Pickup.completed_at >= start)
        .group_by(Donor.id, Donor.name, Donor.type)
        .order_by(func.sum(Pickup.servings_rescued).desc())
        .limit(8)
    ).all()
    top_donors = [
        TopDonor(
            donor_id=r[0],
            name=r[1],
            type=(r[2].value if hasattr(r[2], "value") else str(r[2])),
            meals=int(r[3]),
            rescues=int(r[4]),
        )
        for r in donor_rows
    ]

    return TrendsResponse(
        range_days=range_days,
        series=series,
        by_category=by_category,
        top_donors=top_donors,
    )

"""Impact dashboard schemas (KPIs + trends)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.models.enums import FoodCategory


class StatDelta(BaseModel):
    """A KPI value with its percentage change vs the previous period."""

    value: float
    delta_pct: float | None = None  # None when there is no prior period to compare


class ImpactSummary(BaseModel):
    meals_rescued: StatDelta
    kg_saved: StatDelta
    co2e_avoided_kg: StatDelta
    people_served: StatDelta
    # Supporting context (not the four headline cards):
    active_listings: int
    total_donors: int
    total_recipients: int
    window_days: int


class TrendPoint(BaseModel):
    date: date
    meals: int
    kg_saved: float


class CategoryBreakdown(BaseModel):
    category: FoodCategory
    servings: int
    kg_saved: float


class TopDonor(BaseModel):
    donor_id: int
    name: str
    type: str
    meals: int    # total servings rescued (1 serving == 1 meal)
    rescues: int  # number of completed pickups


class TrendsResponse(BaseModel):
    range_days: int
    series: list[TrendPoint]
    by_category: list[CategoryBreakdown]
    top_donors: list[TopDonor]

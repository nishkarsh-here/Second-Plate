"""Freshness-urgency scoring.

A deliberately transparent function — no model — so the green/amber/rose badge
is explainable by inspection. Urgency rises as a listing nears expiry, scaled by
how perishable its category is and how many servings are at risk.

    score = 100 * clip(0.65 * time_pressure
                       + 0.20 * perishability
                       + 0.15 * size_pressure)

where ``time_pressure`` grows from 0 (just posted) to 1 (at expiry) over a
category-specific horizon (cooked food gets urgent fastest).
"""
from __future__ import annotations

from datetime import datetime

from app.core.time import as_utc, utcnow
from app.models.enums import FoodCategory
from app.schemas.listing import UrgencyInfo

# How perishable each category is (0..1). Cooked food spoils fastest.
PERISHABILITY: dict[FoodCategory, float] = {
    FoodCategory.cooked: 1.00,
    FoodCategory.produce: 0.75,
    FoodCategory.bakery: 0.55,
    FoodCategory.packaged: 0.30,
}

# Minutes over which time-pressure ramps from 0 -> 1 for each category.
HORIZON_MINUTES: dict[FoodCategory, int] = {
    FoodCategory.cooked: 240,      # 4h
    FoodCategory.produce: 480,     # 8h
    FoodCategory.bakery: 720,      # 12h
    FoodCategory.packaged: 2880,   # 48h
}

# Servings at which "size pressure" saturates.
SIZE_SATURATION = 80.0


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _humanize(minutes: int) -> str:
    if minutes <= 0:
        ago = -minutes
        if ago < 60:
            return f"Expired {ago}m ago"
        return f"Expired {ago // 60}h {ago % 60:02d}m ago"
    if minutes < 60:
        return f"Expires in {minutes}m"
    if minutes < 60 * 24:
        return f"Expires in {minutes // 60}h {minutes % 60:02d}m"
    days = minutes // (60 * 24)
    hours = (minutes % (60 * 24)) // 60
    return f"Expires in {days}d {hours}h"


def compute_urgency(
    category: FoodCategory | str,
    servings: int,
    expires_at: datetime,
    now: datetime | None = None,
) -> UrgencyInfo:
    now = now or utcnow()
    cat = FoodCategory(category)
    minutes = int((as_utc(expires_at) - now).total_seconds() // 60)

    if minutes <= 0:
        return UrgencyInfo(
            score=100.0,
            level="expired",
            color="rose",
            minutes_to_expiry=minutes,
            label=_humanize(minutes),
        )

    time_pressure = _clamp(1 - minutes / HORIZON_MINUTES[cat])
    size_pressure = _clamp(servings / SIZE_SATURATION)
    raw = 0.65 * time_pressure + 0.20 * PERISHABILITY[cat] + 0.15 * size_pressure
    score = round(100 * _clamp(raw), 1)

    if score >= 70:
        level, color = "critical", "rose"
    elif score >= 40:
        level, color = "soon", "amber"
    else:
        level, color = "fresh", "green"

    return UrgencyInfo(
        score=score,
        level=level,
        color=color,
        minutes_to_expiry=minutes,
        label=_humanize(minutes),
    )

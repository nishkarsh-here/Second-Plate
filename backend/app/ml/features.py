"""Feature engineering for the surplus forecaster.

This module is the single source of truth for:
  * the holiday/event calendar (shared with the seeder so the injected signal
    and the model's features line up exactly), and
  * how raw ``donation_history`` rows become model features.

The target is next-day servings. To avoid leakage, every rolling/lag feature is
shifted so a row for date *t* only sees data strictly before *t*.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Donor, DonationHistory

# Recurring (month, day) holidays/festivals that drive surplus surges. Shared by
# the seeder (to inject signal) and the model (to learn it) -> a real, learnable
# feature rather than noise.
HOLIDAYS: set[tuple[int, int]] = {
    (1, 1), (1, 26), (3, 8), (4, 14), (5, 1), (8, 15),
    (8, 19), (10, 2), (10, 12), (11, 1), (11, 14), (12, 25), (12, 31),
}

# Feature column order — fixed, because the model and explainability rely on it.
FEATURES: list[str] = [
    "is_restaurant",
    "is_canteen",
    "is_hostel",
    "is_event",
    "day_of_week",
    "is_weekend",
    "month",
    "is_holiday",
    "lag1",
    "lag7",
    "roll7",
    "roll30",
    "trend",
]

# Human-readable labels for the Predictions explainability drawer.
FEATURE_LABELS: dict[str, str] = {
    "is_restaurant": "Donor is a restaurant",
    "is_canteen": "Donor is a canteen",
    "is_hostel": "Donor is a hostel",
    "is_event": "Donor is an event venue",
    "day_of_week": "Day of week",
    "is_weekend": "Weekend",
    "month": "Month / season",
    "is_holiday": "Holiday or festival",
    "lag1": "Yesterday's servings",
    "lag7": "Same day last week",
    "roll7": "7-day average",
    "roll30": "30-day average",
    "trend": "Recent trend (7d vs 30d)",
}

DONOR_TYPES = ["restaurant", "canteen", "hostel", "event"]


def is_holiday(d: date) -> bool:
    return (d.month, d.day) in HOLIDAYS


def load_history_frame(db: Session) -> pd.DataFrame:
    """Tidy frame of every donation-history row joined to its donor."""
    rows = db.execute(
        select(
            DonationHistory.donor_id,
            Donor.name,
            Donor.type,
            DonationHistory.date,
            DonationHistory.servings_donated,
        ).join(Donor, Donor.id == DonationHistory.donor_id)
    ).all()

    df = pd.DataFrame(
        rows, columns=["donor_id", "donor_name", "type", "date", "servings"]
    )
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["type"] = df["type"].map(lambda t: t.value if hasattr(t, "value") else str(t))
    df["servings"] = df["servings"].astype(float)
    return df.sort_values(["donor_id", "date"]).reset_index(drop=True)


def _calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df["day_of_week"] = df["date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["month"] = df["date"].dt.month
    df["is_holiday"] = df["date"].map(lambda d: 1 if (d.month, d.day) in HOLIDAYS else 0)
    for t in DONOR_TYPES:
        df[f"is_{t}"] = (df["type"] == t).astype(int)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag/rolling/calendar features (shifted to prevent target leakage)."""
    df = df.sort_values(["donor_id", "date"]).copy()
    grp = df.groupby("donor_id")["servings"]

    df["lag1"] = grp.shift(1)
    df["lag7"] = grp.shift(7)
    df["roll7"] = grp.transform(lambda s: s.shift(1).rolling(7, min_periods=3).mean())
    df["roll30"] = grp.transform(lambda s: s.shift(1).rolling(30, min_periods=7).mean())
    df["trend"] = df["roll7"] - df["roll30"]

    return _calendar_features(df)


def build_training_matrix(db: Session) -> pd.DataFrame:
    """Full, feature-complete frame ready for train/test splitting."""
    df = add_features(load_history_frame(db))
    if df.empty:
        return df
    return df.dropna(subset=FEATURES).reset_index(drop=True)


def build_prediction_row(donor_history: pd.DataFrame, target_date: date) -> dict:
    """Feature dict for predicting ``target_date`` from one donor's history."""
    s = donor_history.sort_values("date")["servings"].reset_index(drop=True)
    donor_type = donor_history["type"].iloc[0]

    lag1 = float(s.iloc[-1])
    lag7 = float(s.iloc[-7]) if len(s) >= 7 else float(s.mean())
    roll7 = float(s.iloc[-7:].mean())
    roll30 = float(s.iloc[-30:].mean())

    row = {
        "day_of_week": target_date.weekday(),
        "is_weekend": int(target_date.weekday() >= 5),
        "month": target_date.month,
        "is_holiday": int(is_holiday(target_date)),
        "lag1": lag1,
        "lag7": lag7,
        "roll7": roll7,
        "roll30": roll30,
        "trend": roll7 - roll30,
    }
    for t in DONOR_TYPES:
        row[f"is_{t}"] = int(donor_type == t)
    return row

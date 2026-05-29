"""Surplus-prediction schemas (forecast, explainability, retrain metrics)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DonorType


class FactorContribution(BaseModel):
    """One feature's role in a donor's prediction."""

    feature: str          # raw feature key, e.g. "roll7"
    label: str            # human label, e.g. "7-day average"
    value: float          # the feature's value for this donor
    contribution: float   # signed contribution to this prediction (servings)
    importance: float     # global model importance, 0..1


class SurplusPrediction(BaseModel):
    donor_id: int
    donor_name: str
    donor_type: DonorType
    predicted_servings: float
    confidence: float                 # 0..1
    recent_avg_servings: float        # last-7-day average, for context
    top_factors: list[FactorContribution]


class PredictionExplain(BaseModel):
    donor_id: int
    donor_name: str
    predicted_servings: float
    confidence: float
    factors: list[FactorContribution]
    model_version: str
    trained_at: datetime | None


class RetrainMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    n_train: int
    n_test: int
    n_features: int
    feature_importances: dict[str, float]
    trained_at: datetime
    model_version: str

"""Prediction + explainability for the surplus forecaster.

Per-donor next-day forecasts, a transparent confidence score derived from the
donor's recent volatility, and a local feature attribution computed by one-at-a-
time ablation against the training means (no SHAP dependency, fully explainable).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError, NotFoundError
from app.ml import model_store
from app.ml.features import (
    FEATURE_LABELS,
    FEATURES,
    build_prediction_row,
    load_history_frame,
)
from app.models import Donor
from app.schemas.prediction import (
    FactorContribution,
    PredictionExplain,
    SurplusPrediction,
)


def _require_model():
    model, meta = model_store.load()
    if model is None:
        raise BadRequestError("Model not trained yet. Call POST /api/ml/retrain first.")
    return model, meta


def _confidence(servings: pd.Series) -> float:
    """Higher when the donor's recent output is stable (low coefficient of var)."""
    last30 = servings.iloc[-30:]
    mean = float(last30.mean())
    std = float(last30.std(ddof=0))
    cv = std / mean if mean > 0 else 1.0
    return round(min(0.95, max(0.4, 0.95 - cv)), 2)


def _factor_list(model, x_row: pd.DataFrame, meta: dict, top: int | None) -> list[FactorContribution]:
    """Local attribution: how much each feature moves THIS donor's prediction
    versus replacing it with the training mean."""
    importances = meta["feature_importances"]
    means = meta["feature_means"]
    base = float(model.predict(x_row[FEATURES])[0])

    factors: list[FactorContribution] = []
    for feature in FEATURES:
        modified = x_row.copy()
        modified.loc[:, feature] = means[feature]
        ablated = float(model.predict(modified[FEATURES])[0])
        factors.append(
            FactorContribution(
                feature=feature,
                label=FEATURE_LABELS.get(feature, feature),
                value=round(float(x_row.iloc[0][feature]), 2),
                contribution=round(base - ablated, 2),
                importance=round(float(importances.get(feature, 0.0)), 4),
            )
        )

    factors.sort(key=lambda f: abs(f.contribution), reverse=True)
    return factors[:top] if top else factors


def _target_date(group: pd.DataFrame):
    return group["date"].iloc[-1].date() + timedelta(days=1)


def predict_all(db: Session) -> list[SurplusPrediction]:
    model, meta = _require_model()
    df = load_history_frame(db)
    if df.empty:
        return []

    results: list[SurplusPrediction] = []
    for donor_id, group in df.groupby("donor_id"):
        group = group.sort_values("date")
        row = build_prediction_row(group, _target_date(group))
        # All-float so the mean-ablation explainability can overwrite any column
        # (pandas 3.0 refuses float-into-int assignment).
        x_row = pd.DataFrame([row]).astype(float)
        predicted = max(0.0, float(model.predict(x_row[FEATURES])[0]))

        results.append(
            SurplusPrediction(
                donor_id=int(donor_id),
                donor_name=group["donor_name"].iloc[0],
                donor_type=group["type"].iloc[0],
                predicted_servings=round(predicted, 1),
                confidence=_confidence(group["servings"]),
                recent_avg_servings=round(float(group["servings"].iloc[-7:].mean()), 1),
                top_factors=_factor_list(model, x_row, meta, top=4),
            )
        )

    results.sort(key=lambda r: r.predicted_servings, reverse=True)
    return results


def explain(db: Session, donor_id: int) -> PredictionExplain:
    model, meta = _require_model()
    donor = db.get(Donor, donor_id)
    if donor is None:
        raise NotFoundError(f"Donor {donor_id} not found")

    df = load_history_frame(db)
    group = df[df["donor_id"] == donor_id].sort_values("date")
    if group.empty:
        raise BadRequestError(f"No donation history for donor {donor_id}")

    row = build_prediction_row(group, _target_date(group))
    x_row = pd.DataFrame([row]).astype(float)
    predicted = max(0.0, float(model.predict(x_row[FEATURES])[0]))

    return PredictionExplain(
        donor_id=donor_id,
        donor_name=donor.name,
        predicted_servings=round(predicted, 1),
        confidence=_confidence(group["servings"]),
        factors=_factor_list(model, x_row, meta, top=None),
        model_version=meta["model_version"],
        trained_at=datetime.fromisoformat(meta["trained_at"]),
    )

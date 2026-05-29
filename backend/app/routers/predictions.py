"""Surplus prediction endpoints (forecast + explainability)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ml import predict
from app.schemas.prediction import PredictionExplain, SurplusPrediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get(
    "/surplus",
    response_model=list[SurplusPrediction],
    summary="Predicted next-day surplus per donor",
)
def surplus(db: Session = Depends(get_db)) -> list[SurplusPrediction]:
    return predict.predict_all(db)


@router.get(
    "/{donor_id}/explain",
    response_model=PredictionExplain,
    summary="Full feature attribution for one donor's prediction",
)
def explain(donor_id: int = Path(..., ge=1), db: Session = Depends(get_db)) -> PredictionExplain:
    return predict.explain(db, donor_id)

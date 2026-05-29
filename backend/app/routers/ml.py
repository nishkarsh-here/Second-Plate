"""Model lifecycle endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.db.session import get_db
from app.ml import train as train_module
from app.schemas.prediction import RetrainMetrics

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post(
    "/retrain",
    response_model=RetrainMetrics,
    summary="Retrain the surplus model on current data and return metrics",
)
def retrain(db: Session = Depends(get_db)) -> RetrainMetrics:
    try:
        return train_module.train(db)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc

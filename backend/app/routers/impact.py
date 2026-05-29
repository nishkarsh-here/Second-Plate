"""Impact dashboard endpoints (KPIs + trends)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.impact import ImpactSummary, TrendsResponse
from app.services import impact_service

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("/summary", response_model=ImpactSummary, summary="Headline KPIs with deltas")
def impact_summary(
    window_days: int = Query(30, ge=1, le=365, description="Comparison window in days"),
    db: Session = Depends(get_db),
) -> ImpactSummary:
    return impact_service.summary(db, window_days=window_days)


@router.get("/trends", response_model=TrendsResponse, summary="Time series + breakdowns")
def impact_trends(
    range_days: int = Query(30, ge=7, le=365, alias="range", description="Lookback in days"),
    db: Session = Depends(get_db),
) -> TrendsResponse:
    return impact_service.trends(db, range_days=range_days)

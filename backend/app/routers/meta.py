"""Reference data: donors and recipients (for forms, role switcher, claims)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Donor, Recipient
from app.schemas.donor import DonorOut
from app.schemas.recipient import RecipientOut

router = APIRouter(tags=["reference"])


@router.get("/donors", response_model=list[DonorOut], summary="List all donors")
def list_donors(db: Session = Depends(get_db)) -> list[Donor]:
    return list(db.execute(select(Donor).order_by(Donor.name)).scalars().all())


@router.get("/recipients", response_model=list[RecipientOut], summary="List all recipients")
def list_recipients(db: Session = Depends(get_db)) -> list[Recipient]:
    return list(db.execute(select(Recipient).order_by(Recipient.name)).scalars().all())

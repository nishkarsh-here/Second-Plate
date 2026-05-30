"""Registration + authentication logic.

Registering creates a User plus its linked Donor or Recipient profile (so a new
account immediately participates in the marketplace). Location defaults near the
seeded city when not provided.
"""
from __future__ import annotations

import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models import Donor, DonorType, Recipient, RecipientType, User
from app.models.enums import UserRole
from app.schemas.auth import RegisterRequest

CITY_LAT, CITY_LNG = 12.9716, 77.5946


def _jitter(base: float, rng: random.Random) -> float:
    return round(base + rng.uniform(-0.04, 0.04), 6)


def register(db: Session, payload: RegisterRequest) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise ConflictError("An account with this email already exists")

    rng = random.Random(payload.email)
    lat = payload.lat if payload.lat is not None else _jitter(CITY_LAT, rng)
    lng = payload.lng if payload.lng is not None else _jitter(CITY_LNG, rng)

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )

    if payload.role == UserRole.donor:
        donor = Donor(
            name=payload.name,
            type=payload.donor_type or DonorType.restaurant,
            lat=lat,
            lng=lng,
            address="Bengaluru",
        )
        db.add(donor)
        db.flush()
        user.donor_id = donor.id
    else:
        recipient = Recipient(
            name=payload.name,
            type=payload.recipient_type or RecipientType.ngo,
            lat=lat,
            lng=lng,
            capacity=120,
        )
        db.add(recipient)
        db.flush()
        user.recipient_id = recipient.id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    return user

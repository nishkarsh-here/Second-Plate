"""Authentication endpoints: register, login, current user."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    profile = user.donor or user.recipient
    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        name=profile.name if profile else user.email,
        lat=profile.lat if profile else None,
        lng=profile.lng if profile else None,
        donor_id=user.donor_id,
        recipient_id=user.recipient_id,
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a donor or recipient account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.register(db, payload)
    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=_user_out(user))


@router.post("/login", response_model=TokenResponse, summary="Log in with email + password")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate(db, payload.email, payload.password)
    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=_user_out(user))


@router.get("/me", response_model=UserOut, summary="Current authenticated user")
def me(user: User = Depends(get_current_user)) -> UserOut:
    return _user_out(user)

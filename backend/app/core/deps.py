"""Authentication dependencies.

``get_current_user_optional`` powers endpoints that work for guests *and*
authenticated users; ``get_current_user`` requires a valid token.
"""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

_bearer = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    return db.get(User, int(payload["sub"]))


def get_current_user(user: User | None = Depends(get_current_user_optional)) -> User:
    if user is None:
        raise UnauthorizedError("Not authenticated")
    return user

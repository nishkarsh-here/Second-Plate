"""Declarative base shared by every ORM model."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy 2.0 declarative base."""

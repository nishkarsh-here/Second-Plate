"""Custom SQLAlchemy column types.

``UTCDateTime`` guarantees that datetimes are timezone-aware UTC when they leave
the database, regardless of backend. SQLite stores datetimes naively (dropping
tzinfo); PostgreSQL uses ``timestamptz``. Without this, the API would emit
offset-less timestamps on SQLite and the frontend would misparse them as local
time — breaking the freshness countdown. We always bind aware-UTC (correct on
PostgreSQL, harmless on SQLite) and re-attach UTC on the way out.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

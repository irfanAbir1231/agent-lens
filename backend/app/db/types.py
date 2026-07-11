from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.engine import Dialect
from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """Persist datetimes as UTC and return timezone-aware UTC values.

    Internal policy: naive datetimes are interpreted as already being UTC.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> datetime | None:
        if value is None:
            return None

        utc_value = (
            value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        )

        if dialect.name == "sqlite":
            return utc_value.replace(tzinfo=None)
        return utc_value

    def process_result_value(
        self,
        value: datetime | None,
        _: Dialect,
    ) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def ensure_utc_datetime(value: datetime) -> datetime:
    # Internal policy: treat naive datetimes as UTC rather than shifting them.
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _serialize_datetime(value: datetime) -> str:
    return ensure_utc_datetime(value).isoformat().replace("+00:00", "Z")


class AgentLensSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        use_enum_values=True,
        json_encoders={datetime: _serialize_datetime},
    )


class ErrorResponse(AgentLensSchema):
    code: str
    message: str
    details: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None
    request_id: str


class PaginationMetadata(AgentLensSchema):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)

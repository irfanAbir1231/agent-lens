from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import AgentLensSchema, PaginationMetadata


class AuditEventSummary(AgentLensSchema):
    id: str
    action: str
    actor_id: str | None
    actor_role: str | None
    case_id: str | None
    alert_id: str | None
    analysis_id: str | None
    before_status: str | None
    after_status: str | None
    case_version: int | None
    metadata: dict[str, Any]
    created_at: datetime


class AuditEventListResponse(AgentLensSchema):
    events: list[AuditEventSummary]
    pagination: PaginationMetadata

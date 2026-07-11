from __future__ import annotations

from datetime import datetime

from app.schemas.common import AgentLensSchema


class AuditEventSummary(AgentLensSchema):
    id: str
    action: str
    created_at: datetime

from __future__ import annotations

from datetime import datetime

from app.schemas.common import AgentLensSchema
from app.schemas.enums import CaseStatus, HumanDecision


class CaseSummary(AgentLensSchema):
    id: str
    status: CaseStatus
    latest_decision: HumanDecision | None = None
    created_at: datetime

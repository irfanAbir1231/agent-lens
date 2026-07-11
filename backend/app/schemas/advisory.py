from __future__ import annotations

from app.schemas.common import AgentLensSchema
from app.schemas.enums import AIAdvisoryStatus, HumanDecision, UserRole


class AdvisoryAction(AgentLensSchema):
    title: str
    responsible_role: UserRole
    requires_human_approval: bool


class AdvisorySummary(AgentLensSchema):
    advisory_status: AIAdvisoryStatus
    recommended_actions: list[AdvisoryAction]
    latest_human_decision: HumanDecision | None = None

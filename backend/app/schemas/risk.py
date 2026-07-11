from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import AlertType, Severity, UserRole


class RiskAssessment(AgentLensSchema):
    severity: Severity
    alert_type: AlertType
    priority: int = Field(ge=1, le=4)
    reasons: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    allow_ai_advisory: bool
    required_human_role: UserRole
    allowed_actions: list[str]
    prohibited_actions: list[str]
    rule_version: str
    advisory_only: bool = True

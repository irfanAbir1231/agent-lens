from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import AlertType, Severity


class RiskAssessment(AgentLensSchema):
    alert_type: AlertType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)

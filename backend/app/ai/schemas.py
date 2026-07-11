from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import (
    AlertType,
    DataHealthStatus,
    PressureLevel,
    Provider,
    Severity,
    UserRole,
)


class SanitizedEvidence(AgentLensSchema):
    code: str
    description: str
    measured_value: float
    baseline_value: float | None


class SanitizedSource(AgentLensSchema):
    source_id: str
    title: str
    excerpt: str = Field(max_length=500)
    relevance_reason: str


class AdvisoryProviderContext(AgentLensSchema):
    provider: Provider
    data_quality_status: DataHealthStatus
    data_quality_confidence: float = Field(ge=0.0, le=1.0)
    pressure_level: PressureLevel
    forecast_confidence: float = Field(ge=0.0, le=1.0)
    estimated_shortage_minutes: int | None = Field(default=None, ge=0)
    anomaly_score: float = Field(ge=0.0, le=1.0)
    anomaly_evidence: list[SanitizedEvidence]
    legitimate_explanations: list[str]
    limitations: list[str]
    alert_type: AlertType
    severity: Severity
    risk_reasons: list[str]
    required_human_role: UserRole
    allowed_actions: list[str]
    prohibited_actions: list[str]
    policy_sources: list[SanitizedSource]
    similar_cases: list[SanitizedSource]


class SanitizedAdvisoryInput(AgentLensSchema):
    agent_id: str
    analysis_id: str
    providers: list[AdvisoryProviderContext] = Field(min_length=1, max_length=3)

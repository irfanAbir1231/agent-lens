from __future__ import annotations

from datetime import datetime

from app.schemas.anomaly import AnomalyResult
from app.schemas.common import AgentLensSchema, PaginationMetadata
from app.schemas.enums import AlertStatus, AlertType, Provider, Severity
from app.schemas.risk import RiskAssessment


class AlertSummary(AgentLensSchema):
    id: str
    agent_id: str
    provider: Provider
    alert_type: AlertType
    status: AlertStatus
    severity: Severity
    priority: int
    confidence: float
    created_at: datetime


class RetrievalSource(AgentLensSchema):
    source_id: str
    title: str
    excerpt: str
    relevance_reason: str
    permitted_action_categories: list[str]


class AlertDetail(AlertSummary):
    analysis_id: str | None = None
    provider_scope: Provider
    anomaly: AnomalyResult
    risk: RiskAssessment
    limitations: list[str]
    policy_sources: list[RetrievalSource]
    similar_cases: list[RetrievalSource]
    projection_version: str
    is_persisted: bool = False


class AlertListResponse(AgentLensSchema):
    generated_at: datetime
    alerts: list[AlertSummary]
    pagination: PaginationMetadata

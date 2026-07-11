from __future__ import annotations

from datetime import datetime

from app.schemas.advisory import AdvisorySummary
from app.schemas.anomaly import AnomalySummary
from app.schemas.common import AgentLensSchema
from app.schemas.data_quality import ProviderDataHealth
from app.schemas.forecast import ForecastSummary
from app.schemas.risk import RiskAssessment


class AnalysisSummary(AgentLensSchema):
    id: str
    created_at: datetime
    data_quality: list[ProviderDataHealth]
    forecasts: list[ForecastSummary]
    anomaly: AnomalySummary
    risk: RiskAssessment
    advisory: AdvisorySummary

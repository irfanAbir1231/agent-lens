from __future__ import annotations

from datetime import datetime

from app.schemas.common import AgentLensSchema
from app.schemas.enums import AlertStatus, AlertType, Severity


class AlertSummary(AgentLensSchema):
    id: str
    alert_type: AlertType
    status: AlertStatus
    severity: Severity
    created_at: datetime

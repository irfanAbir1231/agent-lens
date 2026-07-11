from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import DataHealthStatus, Provider


class ProviderBalanceSnapshot(AgentLensSchema):
    provider: Provider
    provider_balance_minor: int = Field(ge=0)
    updated_at: datetime


class ProviderFeedStateSummary(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    last_received_at: datetime
    checked_at: datetime
    latency_seconds: int = Field(ge=0)


class ProviderTotalSummary(AgentLensSchema):
    provider: Provider
    total_provider_balance_minor: int = Field(ge=0)


class ProviderFeedSummary(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    agents_reporting: int = Field(ge=0)
    last_received_at: datetime | None = None

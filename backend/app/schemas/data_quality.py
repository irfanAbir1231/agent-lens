from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import DataHealthStatus, Provider


class ProviderDataHealth(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    confidence_multiplier: float = Field(ge=0.0, le=1.0)

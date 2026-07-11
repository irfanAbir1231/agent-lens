from __future__ import annotations

from typing import Literal

from app.schemas.common import AgentLensSchema


class HealthResponse(AgentLensSchema):
    status: Literal["healthy"] = "healthy"
    service: str
    version: str

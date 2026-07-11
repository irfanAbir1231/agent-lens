from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import (
    AIAdvisoryStatus,
    HumanDecision,
    Provider,
    UserRole,
)


class AdvisoryAction(AgentLensSchema):
    rank: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=160)
    rationale: str = Field(min_length=1, max_length=500)
    action_category: str = Field(min_length=1, max_length=80)
    provider: Provider | None = None
    responsible_role: UserRole
    requires_human_approval: Literal[True] = True
    source_ids: list[str]


class AdvisorySourceReference(AgentLensSchema):
    source_id: str
    relevance: str = Field(min_length=1, max_length=300)


class AIAdvisory(AgentLensSchema):
    summary: str = Field(min_length=1, max_length=600)
    operational_assessment: str = Field(min_length=1, max_length=1000)
    why: list[str] = Field(min_length=1, max_length=10)
    recommended_actions: list[AdvisoryAction] = Field(min_length=1, max_length=10)
    responsible_role: UserRole
    source_ids: list[str]
    uncertainty: list[str] = Field(max_length=10)
    human_verification_questions: list[str] = Field(max_length=10)
    source_references: list[AdvisorySourceReference]
    requires_human_review: Literal[True] = True
    prohibited_actions_confirmed: Literal[True] = True


class AdvisorySummary(AgentLensSchema):
    advisory_status: AIAdvisoryStatus
    guidance: AIAdvisory
    model: str | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    error_category: str | None = None
    fallback_reason: str | None = None
    latest_human_decision: HumanDecision | None = None

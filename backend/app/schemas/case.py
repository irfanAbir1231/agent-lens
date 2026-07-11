from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import AgentLensSchema, PaginationMetadata
from app.schemas.enums import CaseStatus, HumanDecision, Provider, Severity, UserRole


class CaseScope(AgentLensSchema):
    scope_type: Literal["PROVIDER", "AGENT"]
    provider: Provider | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> CaseScope:
        if (self.scope_type == "PROVIDER") != (self.provider is not None):
            raise ValueError(
                "Provider scope requires one provider; agent scope forbids it."
            )
        return self


class CaseCapabilities(AgentLensSchema):
    can_assign: bool
    can_acknowledge: bool
    can_add_note: bool
    can_decide: bool
    can_escalate: bool
    can_resolve: bool
    can_dismiss: bool
    assignable_user_ids: list[str]
    allowed_human_decisions: list[HumanDecision]


class CaseNote(AgentLensSchema):
    id: str
    author_id: str
    body: str
    created_at: datetime


class ModifiedAction(AgentLensSchema):
    title: str = Field(min_length=1, max_length=160)
    action_category: str = Field(min_length=1, max_length=80)
    provider: Provider | None = None


class HumanDecisionEntry(AgentLensSchema):
    id: str
    actor_id: str
    decision: HumanDecision
    modified_actions: list[ModifiedAction]
    note: str
    case_version: int
    created_at: datetime


class CaseTimelineEvent(AgentLensSchema):
    id: str
    action: str
    actor_id: str | None
    before_status: str | None
    after_status: str | None
    case_version: int | None
    created_at: datetime


class CaseSummary(AgentLensSchema):
    id: str
    alert_id: str
    analysis_id: str
    agent_id: str
    area_id: str
    scope: CaseScope
    severity: Severity
    priority: int
    required_role: UserRole
    assigned_to: str | None
    status: CaseStatus
    version: int
    latest_decision: HumanDecision | None
    created_at: datetime
    updated_at: datetime


class CaseDetail(CaseSummary):
    allowed_actions: list[str]
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    resolution_category: str | None
    resolution_note: str | None
    dismissal_reason: str | None
    notes: list[CaseNote]
    decisions: list[HumanDecisionEntry]
    timeline: list[CaseTimelineEvent]
    capabilities: CaseCapabilities


class CaseListResponse(AgentLensSchema):
    cases: list[CaseSummary]
    pagination: PaginationMetadata


class VersionedCaseRequest(AgentLensSchema):
    expected_status: CaseStatus
    expected_version: int = Field(ge=1)


class AssignCaseRequest(VersionedCaseRequest):
    assignee_id: str


class AddCaseNoteRequest(VersionedCaseRequest):
    body: str = Field(min_length=1, max_length=2000)


class EscalateCaseRequest(VersionedCaseRequest):
    reason: str = Field(min_length=1, max_length=1000)


class HumanDecisionRequest(VersionedCaseRequest):
    decision: HumanDecision
    modified_actions: list[ModifiedAction] = Field(default_factory=list, max_length=10)
    note: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def validate_modification(self) -> HumanDecisionRequest:
        if self.decision == HumanDecision.MODIFIED and not self.modified_actions:
            raise ValueError("MODIFIED requires at least one modified action.")
        if self.decision != HumanDecision.MODIFIED and self.modified_actions:
            raise ValueError("Modified actions are allowed only for MODIFIED.")
        return self


class ResolveCaseRequest(VersionedCaseRequest):
    resolution_category: str = Field(min_length=1, max_length=64)
    resolution_note: str = Field(min_length=1, max_length=2000)


class DismissCaseRequest(VersionedCaseRequest):
    reason: str = Field(min_length=1, max_length=2000)

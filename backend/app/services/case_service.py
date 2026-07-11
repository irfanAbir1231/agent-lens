from __future__ import annotations

from datetime import UTC, datetime
from math import ceil

from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.authorization import policy
from app.authorization.sanitization import validate_workflow_text
from app.core.errors import AppError
from app.core.security import Principal
from app.db.models import CaseRecord, SyntheticUser
from app.repositories.case_repository import CaseRepository, decision_fingerprint
from app.schemas.case import (
    AddCaseNoteRequest,
    AssignCaseRequest,
    CaseCapabilities,
    CaseDetail,
    CaseListResponse,
    CaseNote,
    CaseScope,
    CaseSummary,
    CaseTimelineEvent,
    DismissCaseRequest,
    EscalateCaseRequest,
    HumanDecisionEntry,
    HumanDecisionRequest,
    ModifiedAction,
    ResolveCaseRequest,
    VersionedCaseRequest,
)
from app.schemas.common import PaginationMetadata
from app.schemas.enums import (
    CaseStatus,
    HumanDecision,
    Provider,
    Severity,
    UserRole,
)


class CaseService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = CaseRepository(session)
        self._audit = AuditService(session)

    def list_cases(
        self,
        principal: Principal,
        *,
        status: CaseStatus | None,
        provider: Provider | None,
        agent_id: str | None,
        page: int,
        page_size: int,
    ) -> CaseListResponse:
        cases = [
            item
            for item in self._repository.list_cases()
            if policy.can_view(principal, item)
        ]
        cases = [
            item
            for item in cases
            if (status is None or item.status == status.value)
            and (provider is None or item.provider == provider.value)
            and (agent_id is None or item.agent_id == agent_id)
        ]
        start = (page - 1) * page_size
        return CaseListResponse(
            cases=[self._summary(item) for item in cases[start : start + page_size]],
            pagination=PaginationMetadata(
                page=page,
                page_size=page_size,
                total_items=len(cases),
                total_pages=ceil(len(cases) / page_size) if cases else 0,
            ),
        )

    def get_case(self, principal: Principal, case_id: str) -> CaseDetail:
        case = self._repository.get(case_id)
        self._require(principal, case, policy.can_view(principal, case), "VIEW_CASE")
        return self._detail(principal, case)

    def assign(
        self, principal: Principal, case_id: str, request: AssignCaseRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_assign(principal, case), "ASSIGN_CASE"
        )
        assignee = self._repository.user(request.assignee_id)
        if (
            assignee is None
            or not assignee.is_active
            or not self._assignable(case, assignee)
        ):
            raise AppError(
                status_code=422,
                code="invalid_assignee",
                message="The requested assignee is not eligible for this case.",
            )
        if (
            principal.role in {UserRole.RISK_ANALYST, UserRole.PROVIDER_OPERATIONS}
            and assignee.id != principal.id
        ):
            self._deny(principal, case, "ASSIGN_OTHER_USER")
        if case.assigned_to is not None and principal.role not in {
            UserRole.SYSTEM_ADMIN,
            UserRole.AREA_MANAGER,
        }:
            self._deny(principal, case, "REASSIGN_CASE")
        before = case.status
        was_unassigned = case.assigned_to is None
        new_status = (
            CaseStatus.ASSIGNED.value
            if case.status == CaseStatus.NEW.value
            else case.status
        )
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={"assigned_to": assignee.id, "status": new_status},
        )
        self._audit.record(
            "CASE_ASSIGNED" if was_unassigned else "OWNERSHIP_CHANGED",
            principal=principal,
            case_id=case.id,
            alert_id=case.alert_id,
            before_status=before,
            after_status=new_status,
            case_version=updated.version,
            metadata={"assignee_id": assignee.id},
        )
        return self._commit_detail(principal, updated)

    def acknowledge(
        self, principal: Principal, case_id: str, request: VersionedCaseRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_acknowledge(principal, case), "ACKNOWLEDGE_CASE"
        )
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={"status": CaseStatus.ACKNOWLEDGED.value, "acknowledged_at": _now()},
        )
        self._audit.record(
            "CASE_ACKNOWLEDGED",
            principal=principal,
            case_id=case.id,
            before_status=case.status,
            after_status=CaseStatus.ACKNOWLEDGED.value,
            case_version=updated.version,
        )
        return self._commit_detail(principal, updated)

    def add_note(
        self, principal: Principal, case_id: str, request: AddCaseNoteRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(principal, case, policy.can_note(principal, case), "ADD_NOTE")
        note = self._repository.add_note(
            case.id, principal.id, validate_workflow_text(request.body)
        )
        updated = self._repository.transition(
            case, expected_version=request.expected_version, values={}
        )
        self._audit.record(
            "NOTE_ADDED",
            principal=principal,
            case_id=case.id,
            case_version=updated.version,
            metadata={"note_id": note.id},
        )
        return self._commit_detail(principal, updated)

    def escalate(
        self, principal: Principal, case_id: str, request: EscalateCaseRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_escalate(principal, case), "ESCALATE_CASE"
        )
        reason = self._repository.add_note(
            case.id, principal.id, validate_workflow_text(request.reason)
        )
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={"status": CaseStatus.ESCALATED.value},
        )
        self._audit.record(
            "CASE_ESCALATED",
            principal=principal,
            case_id=case.id,
            before_status=case.status,
            after_status=CaseStatus.ESCALATED.value,
            case_version=updated.version,
            metadata={"reason_note_id": reason.id},
        )
        return self._commit_detail(principal, updated)

    def decide(
        self, principal: Principal, case_id: str, request: HumanDecisionRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_decide(principal, case), "HUMAN_DECISION"
        )
        note = validate_workflow_text(request.note)
        actions = [item.model_dump(mode="json") for item in request.modified_actions]
        for action in request.modified_actions:
            if (
                action.action_category not in case.allowed_actions
                or (case.scope_type == "PROVIDER" and action.provider != case.provider)
                or (case.scope_type == "AGENT" and action.provider is not None)
            ):
                raise AppError(
                    status_code=422,
                    code="modified_action_not_allowed",
                    message=(
                        "A modified action is outside the deterministic case "
                        "allowlist or scope."
                    ),
                )
        fingerprint = decision_fingerprint(
            case.id, str(request.decision), actions, note
        )
        decision = self._repository.add_decision(
            case_id=case.id,
            actor_id=principal.id,
            decision=str(request.decision),
            modified_actions=actions,
            note=note,
            fingerprint=fingerprint,
            case_version=case.version + 1,
        )
        next_status = (
            CaseStatus.ESCALATED.value
            if request.decision == HumanDecision.ESCALATED
            else (
                case.status
                if case.status == CaseStatus.ESCALATED.value
                else CaseStatus.UNDER_REVIEW.value
            )
        )
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={"status": next_status},
        )
        self._audit.record(
            "HUMAN_DECISION_RECORDED",
            principal=principal,
            case_id=case.id,
            before_status=case.status,
            after_status=next_status,
            case_version=updated.version,
            metadata={"decision_id": decision.id, "decision": str(request.decision)},
        )
        return self._commit_detail(principal, updated)

    def resolve(
        self, principal: Principal, case_id: str, request: ResolveCaseRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_resolve(principal, case), "RESOLVE_CASE"
        )
        if not self._repository.decisions(case.id):
            raise AppError(
                status_code=409,
                code="human_decision_required",
                message="A human decision is required before resolution.",
            )
        category = validate_workflow_text(request.resolution_category)
        note = validate_workflow_text(request.resolution_note)
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={
                "status": CaseStatus.RESOLVED.value,
                "resolved_at": _now(),
                "resolution_category": category,
                "resolution_note": note,
            },
        )
        self._audit.record(
            "CASE_RESOLVED",
            principal=principal,
            case_id=case.id,
            before_status=case.status,
            after_status=CaseStatus.RESOLVED.value,
            case_version=updated.version,
            metadata={"resolution_category": category},
        )
        return self._commit_detail(principal, updated)

    def dismiss(
        self, principal: Principal, case_id: str, request: DismissCaseRequest
    ) -> CaseDetail:
        case = self._checked(principal, case_id, request)
        self._require(
            principal, case, policy.can_dismiss(principal, case), "DISMISS_CASE"
        )
        reason = validate_workflow_text(request.reason)
        updated = self._repository.transition(
            case,
            expected_version=request.expected_version,
            values={"status": CaseStatus.DISMISSED.value, "dismissal_reason": reason},
        )
        self._audit.record(
            "CASE_DISMISSED",
            principal=principal,
            case_id=case.id,
            before_status=case.status,
            after_status=CaseStatus.DISMISSED.value,
            case_version=updated.version,
            metadata={"reason_recorded": True},
        )
        return self._commit_detail(principal, updated)

    def _checked(
        self, principal: Principal, case_id: str, request: VersionedCaseRequest
    ) -> CaseRecord:
        case = self._repository.get(case_id)
        self._require(principal, case, policy.can_view(principal, case), "VIEW_CASE")
        if (
            case.status != str(request.expected_status)
            or case.version != request.expected_version
        ):
            raise AppError(
                status_code=409,
                code="stale_case_state",
                message="Expected case status or version does not match.",
                details={
                    "current_status": case.status,
                    "current_version": case.version,
                },
            )
        return case

    def _require(
        self, principal: Principal, case: CaseRecord, allowed: bool, action: str
    ) -> None:
        if not allowed:
            self._deny(principal, case, action)

    def _deny(self, principal: Principal, case: CaseRecord, action: str) -> None:
        self._audit.record(
            "AUTHORIZATION_DENIED",
            principal=principal,
            case_id=case.id,
            case_version=case.version,
            metadata={"requested_action": action},
        )
        self._session.commit()
        raise AppError(
            status_code=403,
            code="authorization_denied",
            message="The actor is not authorized for this case action.",
        )

    def _assignable(self, case: CaseRecord, user: SyntheticUser) -> bool:
        principal = _principal(user)
        roles = {UserRole(case.required_role)}
        if UserRole(case.required_role) == UserRole.PROVIDER_OPERATIONS:
            roles.add(UserRole.FIELD_OFFICER)
        return principal.role in roles and policy.in_scope(principal, case)

    def _capabilities(self, principal: Principal, case: CaseRecord) -> CaseCapabilities:
        assignable = (
            [
                item.id
                for item in self._repository.users()
                if self._assignable(case, item)
            ]
            if policy.can_assign(principal, case)
            else []
        )
        return CaseCapabilities(
            can_assign=policy.can_assign(principal, case),
            can_acknowledge=policy.can_acknowledge(principal, case),
            can_add_note=policy.can_note(principal, case),
            can_decide=policy.can_decide(principal, case),
            can_escalate=policy.can_escalate(principal, case),
            can_resolve=policy.can_resolve(principal, case)
            and bool(self._repository.decisions(case.id)),
            can_dismiss=policy.can_dismiss(principal, case),
            assignable_user_ids=assignable,
            allowed_human_decisions=policy.allowed_decisions(principal, case),
        )

    def _summary(self, case: CaseRecord) -> CaseSummary:
        decisions = self._repository.decisions(case.id)
        return CaseSummary(
            id=case.id,
            alert_id=case.alert_id,
            analysis_id=case.analysis_id,
            agent_id=case.agent_id,
            area_id=case.area_id,
            scope=CaseScope(
                scope_type="PROVIDER" if case.provider is not None else "AGENT",
                provider=Provider(case.provider) if case.provider is not None else None,
            ),
            severity=Severity(case.severity),
            priority=case.priority,
            required_role=UserRole(case.required_role),
            assigned_to=case.assigned_to,
            status=CaseStatus(case.status),
            version=case.version,
            latest_decision=(
                HumanDecision(decisions[-1].decision) if decisions else None
            ),
            created_at=case.created_at,
            updated_at=case.updated_at,
        )

    def _detail(self, principal: Principal, case: CaseRecord) -> CaseDetail:
        base = self._summary(case).model_dump()
        return CaseDetail(
            **base,
            allowed_actions=case.allowed_actions,
            acknowledged_at=case.acknowledged_at,
            resolved_at=case.resolved_at,
            resolution_category=case.resolution_category,
            resolution_note=case.resolution_note,
            dismissal_reason=case.dismissal_reason,
            notes=[
                CaseNote(
                    id=item.id,
                    author_id=item.author_id,
                    body=item.body,
                    created_at=item.created_at,
                )
                for item in self._repository.notes(case.id)
            ],
            decisions=[
                HumanDecisionEntry(
                    id=item.id,
                    actor_id=item.actor_id,
                    decision=HumanDecision(item.decision),
                    modified_actions=[
                        ModifiedAction.model_validate(value)
                        for value in item.modified_actions
                    ],
                    note=item.note,
                    case_version=item.case_version,
                    created_at=item.created_at,
                )
                for item in self._repository.decisions(case.id)
            ],
            timeline=[
                CaseTimelineEvent(
                    id=item.id,
                    action=item.action,
                    actor_id=item.actor_id,
                    before_status=item.before_status,
                    after_status=item.after_status,
                    case_version=item.case_version,
                    created_at=item.created_at,
                )
                for item in self._repository.events(case.id)
            ],
            capabilities=self._capabilities(principal, case),
        )

    def _commit_detail(self, principal: Principal, case: CaseRecord) -> CaseDetail:
        self._session.commit()
        return self._detail(principal, case)


def _principal(user: SyntheticUser) -> Principal:
    return Principal(
        user.id,
        user.display_label,
        UserRole(user.role),
        tuple(Provider(item) for item in user.provider_scopes),
        tuple(user.area_scopes),
        tuple(user.agent_scopes),
    )


def _now() -> datetime:
    return datetime.now(UTC)

from __future__ import annotations

from app.core.security import Principal
from app.db.models import CaseRecord
from app.schemas.enums import CaseStatus, HumanDecision, Provider, UserRole

TERMINAL = {CaseStatus.RESOLVED, CaseStatus.DISMISSED}
DECISION_ROLES = {
    UserRole.SYSTEM_ADMIN,
    UserRole.AREA_MANAGER,
    UserRole.RISK_ANALYST,
    UserRole.PROVIDER_OPERATIONS,
}


def in_scope(principal: Principal, case: CaseRecord) -> bool:
    if principal.role == UserRole.SYSTEM_ADMIN:
        return True
    if principal.providers and (
        case.provider is None or Provider(case.provider) not in principal.providers
    ):
        return False
    if principal.areas and case.area_id not in principal.areas:
        return False
    if principal.agents and case.agent_id not in principal.agents:
        return False
    return True


def can_view(principal: Principal, case: CaseRecord) -> bool:
    return in_scope(principal, case)


def can_assign(principal: Principal, case: CaseRecord) -> bool:
    if not in_scope(principal, case) or CaseStatus(case.status) in TERMINAL:
        return False
    if case.assigned_to is not None:
        return principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
    if principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}:
        return True
    return principal.role == UserRole(case.required_role)


def is_assignee(principal: Principal, case: CaseRecord) -> bool:
    return case.assigned_to == principal.id


def can_acknowledge(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and is_assignee(principal, case)
        and case.status == CaseStatus.ASSIGNED.value
    )


def can_note(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and case.assigned_to is not None
        and CaseStatus(case.status) not in TERMINAL
        and (
            is_assignee(principal, case)
            or principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
        )
    )


def can_decide(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and principal.role in DECISION_ROLES
        and case.status
        in {
            CaseStatus.ACKNOWLEDGED.value,
            CaseStatus.UNDER_REVIEW.value,
            CaseStatus.ESCALATED.value,
        }
        and (
            is_assignee(principal, case)
            or principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
        )
    )


def can_escalate(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and case.status
        in {CaseStatus.ACKNOWLEDGED.value, CaseStatus.UNDER_REVIEW.value}
        and (
            is_assignee(principal, case)
            or principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
        )
    )


def can_resolve(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and principal.role in DECISION_ROLES
        and case.status in {CaseStatus.UNDER_REVIEW.value, CaseStatus.ESCALATED.value}
        and (
            is_assignee(principal, case)
            or principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
        )
    )


def can_dismiss(principal: Principal, case: CaseRecord) -> bool:
    return (
        in_scope(principal, case)
        and principal.role in {UserRole.SYSTEM_ADMIN, UserRole.AREA_MANAGER}
        and CaseStatus(case.status) not in TERMINAL
    )


def allowed_decisions(principal: Principal, case: CaseRecord) -> list[HumanDecision]:
    return list(HumanDecision) if can_decide(principal, case) else []

from __future__ import annotations

from app.schemas.enums import (
    AIAdvisoryStatus,
    AlertStatus,
    AlertType,
    CaseStatus,
    DataHealthStatus,
    HumanDecision,
    PressureLevel,
    Provider,
    Severity,
    UserRole,
)


def test_protected_enums_match_guideline_contract() -> None:
    assert [member.value for member in Provider] == ["BKASH", "NAGAD", "ROCKET"]
    assert [member.value for member in UserRole] == [
        "AGENT",
        "PROVIDER_OPERATIONS",
        "FIELD_OFFICER",
        "RISK_ANALYST",
        "AREA_MANAGER",
        "MANAGEMENT_VIEWER",
        "SYSTEM_ADMIN",
    ]
    assert [member.value for member in AlertType] == [
        "LIQUIDITY_PRESSURE",
        "UNUSUAL_ACTIVITY",
        "DATA_QUALITY",
        "COMBINED_OPERATIONAL_REVIEW",
    ]
    assert [member.value for member in AlertStatus] == [
        "NEW",
        "TRIAGED",
        "ASSIGNED",
        "ACKNOWLEDGED",
        "UNDER_REVIEW",
        "ESCALATED",
        "RESOLVED",
        "DISMISSED",
    ]
    assert [member.value for member in CaseStatus] == [
        "NEW",
        "ASSIGNED",
        "ACKNOWLEDGED",
        "UNDER_REVIEW",
        "ESCALATED",
        "RESOLVED",
        "DISMISSED",
    ]
    assert [member.value for member in Severity] == [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ]
    assert [member.value for member in PressureLevel] == [
        "NORMAL",
        "WATCH",
        "HIGH",
        "CRITICAL",
        "UNKNOWN",
    ]
    assert [member.value for member in DataHealthStatus] == [
        "HEALTHY",
        "DELAYED",
        "INCOMPLETE",
        "CONFLICTING",
        "UNAVAILABLE",
    ]
    assert [member.value for member in AIAdvisoryStatus] == [
        "NOT_REQUESTED",
        "PENDING",
        "COMPLETED",
        "FAILED",
        "BLOCKED_BY_DATA_QUALITY",
        "REQUIRES_HUMAN_REVIEW",
    ]
    assert [member.value for member in HumanDecision] == [
        "APPROVED",
        "MODIFIED",
        "REJECTED",
        "ESCALATED",
        "CONTINUE_MONITORING",
    ]

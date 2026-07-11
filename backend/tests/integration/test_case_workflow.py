from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from app.schemas.enums import ScenarioId
from tests.utils import async_test_client

RISK = {"X-Actor-ID": "USER-RISK-001"}
ADMIN = {"X-Actor-ID": "USER-SYS-001"}


async def _create_case(client):  # type: ignore[no-untyped-def]
    analysis = await client.post(
        "/api/v1/agents/AGENT-104/analysis",
        headers={"Idempotency-Key": "case-flow"},
    )
    assert analysis.status_code == 200
    listed = await client.get("/api/v1/cases", headers=RISK)
    assert listed.status_code == 200
    return listed.json()["cases"][0]


@pytest.mark.anyio
async def test_complete_human_review_flow_and_audit(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-complete"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        assert case["scope"] == {"scope_type": "PROVIDER", "provider": "NAGAD"}
        assert case["status"] == "NEW"
        case_id = case["id"]

        assigned = await client.post(
            f"/api/v1/cases/{case_id}/assign",
            headers=RISK,
            json={
                "assignee_id": "USER-RISK-001",
                "expected_status": "NEW",
                "expected_version": 1,
            },
        )
        assert assigned.json()["status"] == "ASSIGNED"
        assert assigned.json()["version"] == 2

        acknowledged = await client.post(
            f"/api/v1/cases/{case_id}/acknowledge",
            headers=RISK,
            json={"expected_status": "ASSIGNED", "expected_version": 2},
        )
        assert acknowledged.json()["status"] == "ACKNOWLEDGED"

        noted = await client.post(
            f"/api/v1/cases/{case_id}/notes",
            headers=RISK,
            json={
                "body": "Provider-side evidence was manually checked.",
                "expected_status": "ACKNOWLEDGED",
                "expected_version": 3,
            },
        )
        assert noted.json()["version"] == 4
        assert len(noted.json()["notes"]) == 1

        decided = await client.post(
            f"/api/v1/cases/{case_id}/human-decision",
            headers=RISK,
            json={
                "decision": "APPROVED",
                "note": "Proceed with permitted manual verification.",
                "expected_status": "ACKNOWLEDGED",
                "expected_version": 4,
            },
        )
        assert decided.json()["status"] == "UNDER_REVIEW"
        assert decided.json()["latest_decision"] == "APPROVED"

        resolved = await client.post(
            f"/api/v1/cases/{case_id}/resolve",
            headers=RISK,
            json={
                "resolution_category": "CONTINUE_MONITORING",
                "resolution_note": "Human review completed; monitoring will continue.",
                "expected_status": "UNDER_REVIEW",
                "expected_version": 5,
            },
        )
        assert resolved.json()["status"] == "RESOLVED"
        assert not any(
            value
            for key, value in resolved.json()["capabilities"].items()
            if key.startswith("can_")
        )

        events = await client.get(
            f"/api/v1/audit-events?case_id={case_id}", headers=RISK
        )
        actions = {item["action"] for item in events.json()["events"]}
        assert {
            "CASE_CREATED",
            "CASE_ASSIGNED",
            "CASE_ACKNOWLEDGED",
            "NOTE_ADDED",
            "HUMAN_DECISION_RECORDED",
            "CASE_RESOLVED",
        } <= actions
        assert "Provider-side evidence" not in str(events.json())


@pytest.mark.anyio
async def test_stale_duplicate_unauthorized_and_unsafe_requests_fail_safely(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-errors"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        case_id = case["id"]

        denied = await client.get(
            f"/api/v1/cases/{case_id}",
            headers={"X-Actor-ID": "USER-BKASH-OPS"},
        )
        assert denied.status_code == 403
        audit = await client.get(
            "/api/v1/audit-events?action=AUTHORIZATION_DENIED", headers=ADMIN
        )
        assert audit.json()["pagination"]["total_items"] == 1

        await client.post(
            f"/api/v1/cases/{case_id}/assign",
            headers=RISK,
            json={
                "assignee_id": "USER-RISK-001",
                "expected_status": "NEW",
                "expected_version": 1,
            },
        )
        stale = await client.post(
            f"/api/v1/cases/{case_id}/acknowledge",
            headers=RISK,
            json={"expected_status": "ASSIGNED", "expected_version": 1},
        )
        assert stale.status_code == 409
        assert stale.json()["code"] == "stale_case_state"

        unsafe = await client.post(
            f"/api/v1/cases/{case_id}/notes",
            headers=RISK,
            json={
                "body": "Customer OTP is 1234",
                "expected_status": "ASSIGNED",
                "expected_version": 2,
            },
        )
        assert unsafe.status_code == 422
        assert unsafe.json()["code"] == "unsafe_workflow_text"


@pytest.mark.anyio
async def test_versioned_decisions_allow_history_but_reject_exact_duplicate(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-decisions"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        case_id = case["id"]
        await client.post(
            f"/api/v1/cases/{case_id}/assign",
            headers=RISK,
            json={
                "assignee_id": "USER-RISK-001",
                "expected_status": "NEW",
                "expected_version": 1,
            },
        )
        await client.post(
            f"/api/v1/cases/{case_id}/acknowledge",
            headers=RISK,
            json={"expected_status": "ASSIGNED", "expected_version": 2},
        )
        payload = {
            "decision": "CONTINUE_MONITORING",
            "note": "Continue review with current evidence.",
            "expected_status": "ACKNOWLEDGED",
            "expected_version": 3,
        }
        first = await client.post(
            f"/api/v1/cases/{case_id}/human-decision", headers=RISK, json=payload
        )
        duplicate_payload = {
            **payload,
            "expected_status": "UNDER_REVIEW",
            "expected_version": 4,
        }
        duplicate = await client.post(
            f"/api/v1/cases/{case_id}/human-decision",
            headers=RISK,
            json=duplicate_payload,
        )
        second = await client.post(
            f"/api/v1/cases/{case_id}/human-decision",
            headers=RISK,
            json={
                **duplicate_payload,
                "decision": "ESCALATED",
                "note": "Escalate for additional risk review.",
            },
        )
        assert first.status_code == 200
        assert duplicate.status_code == 409
        assert duplicate.json()["code"] == "duplicate_human_decision"
        assert second.json()["status"] == "ESCALATED"
        assert len(second.json()["decisions"]) == 2


@pytest.mark.anyio
async def test_missing_actor_and_read_only_capabilities(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-identity"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        missing = await client.get(f"/api/v1/cases/{case['id']}")
        viewer = await client.get(
            f"/api/v1/cases/{case['id']}",
            headers={"X-Actor-ID": "USER-VIEW-001"},
        )
        assert missing.status_code == 401
        assert missing.json()["code"] == "actor_required"
        assert viewer.status_code == 200
        assert not any(
            value
            for key, value in viewer.json()["capabilities"].items()
            if key.startswith("can_")
        )


@pytest.mark.anyio
async def test_escalation_reason_is_persisted_and_dismissal_is_terminal(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-escalate"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        case_id = case["id"]
        await client.post(
            f"/api/v1/cases/{case_id}/assign",
            headers=RISK,
            json={
                "assignee_id": "USER-RISK-001",
                "expected_status": "NEW",
                "expected_version": 1,
            },
        )
        await client.post(
            f"/api/v1/cases/{case_id}/acknowledge",
            headers=RISK,
            json={"expected_status": "ASSIGNED", "expected_version": 2},
        )
        escalated = await client.post(
            f"/api/v1/cases/{case_id}/escalate",
            headers=RISK,
            json={
                "reason": "Additional risk review is required.",
                "expected_status": "ACKNOWLEDGED",
                "expected_version": 3,
            },
        )
        assert escalated.json()["status"] == "ESCALATED"
        assert escalated.json()["notes"][0]["body"] == (
            "Additional risk review is required."
        )

        dismissed = await client.post(
            f"/api/v1/cases/{case_id}/dismiss",
            headers=ADMIN,
            json={
                "reason": "Deterministic evidence was verified as a benign test.",
                "expected_status": "ESCALATED",
                "expected_version": 4,
            },
        )
        assert dismissed.json()["status"] == "DISMISSED"
        terminal = await client.post(
            f"/api/v1/cases/{case_id}/notes",
            headers=ADMIN,
            json={
                "body": "This terminal case must remain unchanged.",
                "expected_status": "DISMISSED",
                "expected_version": 5,
            },
        )
        assert terminal.status_code == 403


@pytest.mark.anyio
async def test_modified_decision_rejects_action_outside_allowlist(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="case-modified"
    )
    async with async_test_client(settings) as client:
        case = await _create_case(client)
        case_id = case["id"]
        await client.post(
            f"/api/v1/cases/{case_id}/assign",
            headers=RISK,
            json={
                "assignee_id": "USER-RISK-001",
                "expected_status": "NEW",
                "expected_version": 1,
            },
        )
        await client.post(
            f"/api/v1/cases/{case_id}/acknowledge",
            headers=RISK,
            json={"expected_status": "ASSIGNED", "expected_version": 2},
        )
        rejected = await client.post(
            f"/api/v1/cases/{case_id}/human-decision",
            headers=RISK,
            json={
                "decision": "MODIFIED",
                "modified_actions": [
                    {
                        "title": "Forbidden action",
                        "action_category": "FREEZE_ACCOUNT",
                        "provider": "NAGAD",
                    }
                ],
                "note": "This action must be rejected by the server.",
                "expected_status": "ACKNOWLEDGED",
                "expected_version": 3,
            },
        )
        assert rejected.status_code == 422
        assert rejected.json()["code"] == "modified_action_not_allowed"

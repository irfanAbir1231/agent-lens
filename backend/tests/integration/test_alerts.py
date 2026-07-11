from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from app.schemas.enums import ScenarioId
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_normal_and_eid_activity_do_not_project_alerts(
    make_settings: Callable[..., Settings],
) -> None:
    for scenario in (ScenarioId.NORMAL_DAY, ScenarioId.EID_SPIKE):
        async with async_test_client(
            make_settings(scenario=scenario, suffix=f"alerts-{scenario.value}")
        ) as client:
            response = await client.get("/api/v1/alerts")
            assert response.status_code == 200
            assert response.json()["alerts"] == []


@pytest.mark.anyio
async def test_repeated_activity_alert_detail_is_stable_and_sanitized(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="alerts-repeated"
    )
    async with async_test_client(settings) as client:
        first = (await client.get("/api/v1/alerts?provider=NAGAD")).json()
        second = (await client.get("/api/v1/alerts?provider=NAGAD")).json()
        assert first == second
        alert = first["alerts"][0]
        detail = (await client.get(f"/api/v1/alerts/{alert['id']}")).json()

        assert detail["status"] == "NEW"
        assert detail["is_persisted"] is False
        assert detail["anomaly"]["review_level"] == "PRIORITY_REVIEW"
        assert "REPEATED_AMOUNT_PATTERN" in {
            item["code"] for item in detail["anomaly"]["evidence"]
        }
        assert detail["policy_sources"]
        assert any(
            item["source_id"] == "CASE-SUM-003" for item in detail["similar_cases"]
        )
        assert "SIM-ACC" not in str(detail)


@pytest.mark.anyio
async def test_hidden_nagad_combines_measured_activity_and_liquidity_pressure(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.HIDDEN_NAGAD_SHORTAGE, suffix="alerts-hidden"
    )
    async with async_test_client(settings) as client:
        body = (await client.get("/api/v1/alerts?provider=NAGAD")).json()
        alert = next(item for item in body["alerts"] if item["agent_id"] == "AGENT-104")
        detail = (await client.get(f"/api/v1/alerts/{alert['id']}")).json()

        assert detail["alert_type"] == "COMBINED_OPERATIONAL_REVIEW"
        assert detail["provider"] == "NAGAD"
        assert detail["anomaly"]["evidence"]
        assert "LIQUIDITY_CONCENTRATION" in {
            item["code"] for item in detail["anomaly"]["evidence"]
        }


@pytest.mark.anyio
async def test_conflicting_provider_is_blocked_and_unknown_id_is_structured(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.CONFLICTING_BALANCE, suffix="alerts-conflict"
    )
    async with async_test_client(settings) as client:
        listed = (await client.get("/api/v1/alerts?provider=BKASH")).json()
        alert_id = listed["alerts"][0]["id"]
        detail = (await client.get(f"/api/v1/alerts/{alert_id}")).json()
        assert detail["alert_type"] == "DATA_QUALITY"
        assert detail["anomaly"]["evaluation_blocked"] is True
        assert detail["risk"]["allow_ai_advisory"] is False

        missing = await client.get("/api/v1/alerts/ALERT-UNKNOWN")
        assert missing.status_code == 404
        assert missing.json()["code"] == "alert_not_found"

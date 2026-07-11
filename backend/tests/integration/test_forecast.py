from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from app.schemas.enums import ScenarioId
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_normal_forecast_returns_one_shared_and_three_provider_targets(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="forecast-normal")) as client:
        response = await client.get("/api/v1/agents/AGENT-104/forecast")

        assert response.status_code == 200
        body = response.json()
        assert body["generated_at"].endswith("Z")
        assert body["method_version"] == "liquidity-baseline-v1"
        assert body["forecast_horizon_minutes"] == 60
        assert body["shared_cash_forecast"]["target"] == "SHARED_CASH"
        assert [item["provider"] for item in body["provider_forecasts"]] == [
            "BKASH",
            "NAGAD",
            "ROCKET",
        ]
        assert all(
            item["forecast_blocked"] is False for item in body["provider_forecasts"]
        )
        assert all(item["confidence"] >= 0.8 for item in body["provider_forecasts"])
        assert all(
            item["pressure_level"] == "NORMAL" for item in body["provider_forecasts"]
        )
        assert body["shared_cash_forecast"]["pressure_level"] == "NORMAL"
        assert "anomaly" not in str(body).lower()
        assert "risk_assessment" not in body
        assert "advisory" not in str(body).lower()


@pytest.mark.anyio
async def test_hidden_nagad_shortage_is_provider_specific(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.HIDDEN_NAGAD_SHORTAGE, suffix="forecast-hidden"
    )
    async with async_test_client(settings) as client:
        body = (await client.get("/api/v1/agents/AGENT-104/forecast")).json()

        providers = {item["provider"]: item for item in body["provider_forecasts"]}
        assert providers["NAGAD"]["pressure_level"] == "CRITICAL"
        assert providers["NAGAD"]["estimated_shortage_minutes"] <= 60
        assert providers["NAGAD"]["predicted_net_outflow_minor"] > 0
        assert providers["BKASH"]["pressure_level"] == "NORMAL"
        assert providers["ROCKET"]["pressure_level"] == "NORMAL"


@pytest.mark.anyio
async def test_delayed_rocket_blocks_only_rocket_and_shared_cash(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.DELAYED_ROCKET_FEED, suffix="forecast-delayed"
    )
    async with async_test_client(settings) as client:
        body = (await client.get("/api/v1/agents/AGENT-104/forecast")).json()

        providers = {item["provider"]: item for item in body["provider_forecasts"]}
        assert providers["ROCKET"]["forecast_blocked"] is True
        assert providers["ROCKET"]["pressure_level"] == "UNKNOWN"
        assert providers["ROCKET"]["confidence"] == 0
        assert providers["BKASH"]["forecast_blocked"] is False
        assert providers["NAGAD"]["forecast_blocked"] is False
        assert body["shared_cash_forecast"]["forecast_blocked"] is True


@pytest.mark.anyio
async def test_conflicting_bkash_blocks_only_bkash_and_shared_cash(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.CONFLICTING_BALANCE, suffix="forecast-conflict"
    )
    async with async_test_client(settings) as client:
        body = (await client.get("/api/v1/agents/AGENT-102/forecast")).json()

        providers = {item["provider"]: item for item in body["provider_forecasts"]}
        assert providers["BKASH"]["forecast_blocked"] is True
        assert providers["NAGAD"]["forecast_blocked"] is False
        assert providers["ROCKET"]["forecast_blocked"] is False
        assert body["shared_cash_forecast"]["forecast_blocked"] is True


@pytest.mark.anyio
async def test_eid_context_and_repeated_shared_cash_pressure(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(
        make_settings(scenario=ScenarioId.EID_SPIKE, suffix="forecast-eid")
    ) as client:
        eid = (await client.get("/api/v1/agents/AGENT-104/forecast")).json()
        nagad = next(
            item for item in eid["provider_forecasts"] if item["provider"] == "NAGAD"
        )
        assert any(factor["code"] == "EID_CONTEXT" for factor in nagad["top_factors"])

    async with async_test_client(
        make_settings(
            scenario=ScenarioId.REPEATED_TRANSACTIONS,
            suffix="forecast-repeated",
        )
    ) as client:
        repeated = (await client.get("/api/v1/agents/AGENT-104/forecast")).json()
        assert repeated["shared_cash_forecast"]["pressure_level"] == "CRITICAL"
        assert "fraud" not in str(repeated).lower()


@pytest.mark.anyio
async def test_unknown_agent_uses_structured_404(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="forecast-missing")) as client:
        response = await client.get("/api/v1/agents/UNKNOWN-AGENT/forecast")

        assert response.status_code == 404
        assert response.json() == {
            "code": "agent_not_found",
            "message": "Agent UNKNOWN-AGENT was not found.",
            "details": {"agent_id": "UNKNOWN-AGENT"},
            "request_id": response.headers["X-Request-ID"],
        }

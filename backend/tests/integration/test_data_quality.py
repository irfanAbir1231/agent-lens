from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from app.core.config import Settings
from app.schemas.enums import ScenarioId
from tests.utils import async_test_client

ALL_STATUS_KEYS = {
    "HEALTHY",
    "DELAYED",
    "INCOMPLETE",
    "CONFLICTING",
    "UNAVAILABLE",
}


@pytest.mark.anyio
async def test_data_quality_returns_auditable_contract(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="data-quality")) as client:
        response = await client.get(
            "/api/v1/data-quality", params={"page": 1, "page_size": 2}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["generated_at"] == "2026-04-10T09:30:00Z"
        assert body["active_scenario_id"] == "normal_day"
        assert body["is_synthetic_data"] is True
        assert body["status_counts"] == {
            "HEALTHY": 2,
            "DELAYED": 0,
            "INCOMPLETE": 4,
            "CONFLICTING": 0,
            "UNAVAILABLE": 0,
        }
        assert len(body["results"]) == 2
        assert body["pagination"] == {
            "page": 1,
            "page_size": 2,
            "total_items": 6,
            "total_pages": 3,
        }
        first = body["results"][0]
        assert first["agent_id"] == "AGENT-101"
        assert first["overall_status"] == "HEALTHY"
        assert first["evaluator_version"] == "data-quality-v1"
        assert first["data_window"] == {
            "start_at": "2026-04-10T06:30:00Z",
            "end_at": "2026-04-10T09:30:00Z",
            "recent_window_start_at": "2026-04-10T08:30:00Z",
            "lookback_minutes": 180,
            "recent_window_minutes": 60,
        }
        assert len(first["provider_results"]) == 3
        provider_result = first["provider_results"][0]
        assert set(provider_result) == {
            "provider",
            "status",
            "confidence_multiplier",
            "allow_forecast",
            "allow_ai_advisory",
            "component_scores",
            "issue_codes",
            "issue_descriptions",
            "measured_evidence",
            "data_window",
            "recommended_verification_steps",
        }


@pytest.mark.anyio
async def test_data_quality_filters_and_counts_before_pagination(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="filters")) as client:
        response = await client.get(
            "/api/v1/data-quality",
            params={"provider": "BKASH", "page": 2, "page_size": 2},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status_counts"] == {
            "HEALTHY": 2,
            "DELAYED": 0,
            "INCOMPLETE": 4,
            "CONFLICTING": 0,
            "UNAVAILABLE": 0,
        }
        assert body["pagination"]["total_items"] == 6
        assert [item["agent_id"] for item in body["results"]] == [
            "AGENT-103",
            "AGENT-104",
        ]
        assert all(
            [provider["provider"] for provider in item["provider_results"]] == ["BKASH"]
            for item in body["results"]
        )

        agent_response = await client.get(
            "/api/v1/data-quality",
            params={"agent_id": "AGENT-101", "provider": "NAGAD"},
        )
        assert agent_response.status_code == 200
        agent_body = agent_response.json()
        assert agent_body["status_counts"]["HEALTHY"] == 1
        assert sum(agent_body["status_counts"].values()) == 1

        empty_response = await client.get(
            "/api/v1/data-quality", params={"agent_id": "AGENT-999"}
        )
        assert empty_response.status_code == 200
        empty_body = empty_response.json()
        assert empty_body["results"] == []
        assert set(empty_body["status_counts"]) == ALL_STATUS_KEYS
        assert sum(empty_body["status_counts"].values()) == 0


@pytest.mark.anyio
async def test_delayed_scenario_is_provider_isolated_and_blocks_critical_delay(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.DELAYED_ROCKET_FEED,
        suffix="delayed-data-quality",
    )
    async with async_test_client(settings) as client:
        response = await client.get(
            "/api/v1/data-quality",
            params={"agent_id": "AGENT-101", "provider": "ROCKET"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status_counts"]["DELAYED"] == 1
        result = body["results"][0]
        provider_result = result["provider_results"][0]
        assert result["overall_status"] == "DELAYED"
        assert provider_result["issue_codes"] == ["FEED_DELAYED"]
        assert provider_result["measured_evidence"]["feed_delay_minutes"] == 32
        assert provider_result["allow_forecast"] is False
        assert provider_result["allow_ai_advisory"] is False


@pytest.mark.anyio
async def test_conflicting_scenario_exposes_balance_evidence(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.CONFLICTING_BALANCE,
        suffix="conflicting-data-quality",
    )
    async with async_test_client(settings) as client:
        response = await client.get(
            "/api/v1/data-quality",
            params={"agent_id": "AGENT-102", "provider": "BKASH"},
        )

        assert response.status_code == 200
        provider_result = response.json()["results"][0]["provider_results"][0]
        assert provider_result["status"] == "CONFLICTING"
        assert "BALANCE_CONFLICT" in provider_result["issue_codes"]
        assert (
            provider_result["measured_evidence"]["feed_reported_balance_minor"]
            == 7_900_000
        )
        assert provider_result["measured_evidence"]["ledger_balance_minor"] == 7_250_000
        assert provider_result["allow_forecast"] is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "params",
    [
        {"provider": "UNKNOWN"},
        {"page": 0},
        {"page_size": 0},
    ],
)
async def test_data_quality_rejects_invalid_query_parameters(
    make_settings: Callable[..., Settings], params: dict[str, str | int]
) -> None:
    async with async_test_client(
        make_settings(suffix="invalid-data-quality")
    ) as client:
        response = await client.get("/api/v1/data-quality", params=params)

        assert response.status_code == 422
        assert response.json()["code"] == "request_validation_error"


@pytest.mark.anyio
async def test_pass_one_endpoints_remain_available(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="pass-one-regression")) as client:
        responses = await asyncio.gather(
            client.get("/api/v1/health"),
            client.get("/api/v1/overview"),
            client.get("/api/v1/agents"),
            client.get("/api/v1/agents/AGENT-101"),
        )

        assert [response.status_code for response in responses] == [200, 200, 200, 200]

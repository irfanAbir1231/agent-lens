from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_agents_pagination_returns_contract_data(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get(
            "/api/v1/agents", params={"page": 1, "page_size": 2}
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) == 2
        assert body["pagination"] == {
            "page": 1,
            "page_size": 2,
            "total_items": 6,
            "total_pages": 3,
        }
        assert all(len(item["provider_balances"]) == 3 for item in body["items"])
        assert all(len(item["feed_states"]) == 3 for item in body["items"])


@pytest.mark.anyio
async def test_agents_page_size_is_bounded(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get(
            "/api/v1/agents", params={"page": 1, "page_size": 250}
        )

        assert response.status_code == 200
        assert response.json()["pagination"]["page_size"] == 100


@pytest.mark.anyio
async def test_agent_detail_returns_recent_transactions_and_utc_timestamps(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/agents/AGENT-104")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == "AGENT-104"
        assert body["active_scenario_id"] == "normal_day"
        assert body["is_synthetic_data"] is True
        assert body["recent_transactions"]
        assert body["provider_balances"][0]["updated_at"] == "2026-04-10T09:28:00Z"
        assert body["feed_states"][0]["checked_at"] == "2026-04-10T09:30:00Z"
        assert body["recent_transactions"][0]["occurred_at"].endswith("Z")
        assert "forecasts" not in body
        assert "anomaly" not in body
        assert "risk" not in body
        assert "advisory" not in body
        assert "phone" not in str(body).lower()
        assert "otp" not in str(body).lower()


@pytest.mark.anyio
async def test_unknown_agent_returns_structured_404_with_request_id(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/agents/AGENT-999")

        assert response.status_code == 404
        assert response.headers["X-Request-ID"]
        body = response.json()
        assert set(body) == {"code", "message", "details", "request_id"}
        assert body == {
            "code": "agent_not_found",
            "message": "Agent AGENT-999 was not found.",
            "details": {"agent_id": "AGENT-999"},
            "request_id": response.headers["X-Request-ID"],
        }

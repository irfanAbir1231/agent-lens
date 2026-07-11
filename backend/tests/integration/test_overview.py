from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_overview_returns_seeded_summary(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/overview")

        assert response.status_code == 200
        body = response.json()
        assert body["active_scenario_id"] == "normal_day"
        assert body["agent_count"] == 6
        assert body["is_synthetic_data"] is True
        assert body["generated_at"] == "2026-04-10T09:30:00Z"
        assert len(body["provider_totals"]) == 3
        assert len(body["feed_summary"]) == 3
        assert "forecasts" not in body
        assert "anomaly" not in body
        assert "risk" not in body
        assert "advisory" not in body


@pytest.mark.anyio
async def test_provider_totals_and_shared_cash_are_kept_separate(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/overview")

        assert response.status_code == 200
        body = response.json()
        provider_total_sum = sum(
            item["total_provider_balance_minor"] for item in body["provider_totals"]
        )
        provider_totals = {
            item["provider"]: item["total_provider_balance_minor"]
            for item in body["provider_totals"]
        }
        assert body["total_shared_cash_minor"] > 0
        assert body["total_shared_cash_minor"] == 26_200_000
        assert provider_totals == {
            "BKASH": 42_600_000,
            "NAGAD": 29_200_000,
            "ROCKET": 26_640_000,
        }
        assert provider_total_sum > body["total_shared_cash_minor"]
